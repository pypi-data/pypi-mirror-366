"""Security features for gdmongolite - Authentication, Authorization, Encryption"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from .core import Schema, DB
from .exceptions import GDMongoError


class PasswordManager:
    """Secure password hashing and verification"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password securely"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_salt(self) -> str:
        """Generate a random salt"""
        return secrets.token_hex(32)


class JWTManager:
    """JWT token management"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
    
    def create_access_token(
        self, 
        data: Dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


class RoleBasedAccessControl:
    """Role-based access control system"""
    
    def __init__(self):
        self.roles = {}
        self.permissions = {}
        self.user_roles = {}
    
    def define_role(self, role_name: str, permissions: List[str]):
        """Define a role with permissions"""
        self.roles[role_name] = permissions
        for permission in permissions:
            if permission not in self.permissions:
                self.permissions[permission] = []
            self.permissions[permission].append(role_name)
    
    def assign_role(self, user_id: str, role: str):
        """Assign role to user"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        if role not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role)
    
    def remove_role(self, user_id: str, role: str):
        """Remove role from user"""
        if user_id in self.user_roles and role in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role)
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        user_roles = self.user_roles.get(user_id, [])
        for role in user_roles:
            if permission in self.roles.get(role, []):
                return True
        return False
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for user"""
        permissions = set()
        user_roles = self.user_roles.get(user_id, [])
        for role in user_roles:
            permissions.update(self.roles.get(role, []))
        return list(permissions)


class DataEncryption:
    """Data encryption for sensitive fields"""
    
    def __init__(self, key: bytes = None):
        from cryptography.fernet import Fernet
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if isinstance(data, str):
            data = data.encode()
        encrypted = self.cipher.encrypt(data)
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode()
    
    def encrypt_dict(self, data: Dict, fields_to_encrypt: List[str]) -> Dict:
        """Encrypt specific fields in dictionary"""
        encrypted_data = data.copy()
        for field in fields_to_encrypt:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data
    
    def decrypt_dict(self, data: Dict, fields_to_decrypt: List[str]) -> Dict:
        """Decrypt specific fields in dictionary"""
        decrypted_data = data.copy()
        for field in fields_to_decrypt:
            if field in decrypted_data:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        return decrypted_data


class SecurityMiddleware:
    """Security middleware for FastAPI"""
    
    def __init__(self, db: DB):
        self.db = db
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()
        self.rbac = RoleBasedAccessControl()
        self.encryption = DataEncryption()
        self.security = HTTPBearer()
        
        # Define default roles
        self._setup_default_roles()
    
    def _setup_default_roles(self):
        """Setup default roles and permissions"""
        self.rbac.define_role("admin", [
            "read", "write", "delete", "manage_users", "manage_roles"
        ])
        self.rbac.define_role("user", ["read", "write"])
        self.rbac.define_role("readonly", ["read"])
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        """Get current authenticated user"""
        token = credentials.credentials
        payload = self.jwt_manager.verify_token(token)
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database (assuming User schema exists)
        if hasattr(self.db, 'User'):
            user = await self.db.User.find(_id=user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            return user
        
        return {"_id": user_id, **payload}
    
    def require_permission(self, permission: str):
        """Decorator to require specific permission"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get current user from kwargs or dependency injection
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user_id = str(current_user.get("_id"))
                if not self.rbac.has_permission(user_id, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission '{permission}' required"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_role(self, role: str):
        """Decorator to require specific role"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user_id = str(current_user.get("_id"))
                user_roles = self.rbac.user_roles.get(user_id, [])
                if role not in user_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role '{role}' required"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username/password"""
        if not hasattr(self.db, 'User'):
            raise GDMongoError("User schema not found")
        
        user = await self.db.User.find(username=username).first()
        if not user:
            return None
        
        if not self.password_manager.verify_password(password, user.get("password_hash", "")):
            return None
        
        return user
    
    async def register_user(
        self, 
        username: str, 
        password: str, 
        email: str, 
        role: str = "user",
        **extra_fields
    ) -> Dict:
        """Register new user"""
        if not hasattr(self.db, 'User'):
            raise GDMongoError("User schema not found")
        
        # Check if user exists
        existing_user = await self.db.User.find(username=username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Hash password
        password_hash = self.password_manager.hash_password(password)
        
        # Create user
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "is_active": True,
            **extra_fields
        }
        
        response = await self.db.User.insert(user_data)
        if response.success:
            user_id = str(response.data)
            self.rbac.assign_role(user_id, role)
            return {"user_id": user_id, "username": username, "role": role}
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    def create_login_token(self, user: Dict) -> str:
        """Create login token for user"""
        token_data = {
            "sub": str(user["_id"]),
            "username": user.get("username"),
            "email": user.get("email"),
            "iat": datetime.utcnow()
        }
        return self.jwt_manager.create_access_token(token_data)


class AuditLog:
    """Audit logging for security events"""
    
    def __init__(self, db: DB):
        self.db = db
    
    async def log_event(
        self, 
        event_type: str, 
        user_id: str = None, 
        details: Dict = None,
        ip_address: str = None
    ):
        """Log security event"""
        log_entry = {
            "event_type": event_type,
            "user_id": user_id,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.utcnow()
        }
        
        # Create audit log collection if it doesn't exist
        if not hasattr(self.db, 'AuditLog'):
            class AuditLogSchema(Schema):
                event_type: str
                user_id: Optional[str] = None
                details: Dict = {}
                ip_address: Optional[str] = None
                timestamp: datetime
            
            self.db.register_schema(AuditLogSchema)
        
        await self.db.AuditLogSchema.insert(log_entry)
    
    async def get_user_activity(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user activity logs"""
        if hasattr(self.db, 'AuditLogSchema'):
            return await (self.db.AuditLogSchema
                         .find(user_id=user_id)
                         .sort("-timestamp")
                         .limit(limit)
                         .to_list())
        return []
    
    async def get_security_events(
        self, 
        event_types: List[str] = None, 
        hours: int = 24
    ) -> List[Dict]:
        """Get recent security events"""
        if hasattr(self.db, 'AuditLogSchema'):
            since = datetime.utcnow() - timedelta(hours=hours)
            query = {"timestamp__gte": since}
            
            if event_types:
                query["event_type__in"] = event_types
            
            return await (self.db.AuditLogSchema
                         .find(**query)
                         .sort("-timestamp")
                         .to_list())
        return []


class SecurityConfig:
    """Security configuration and best practices"""
    
    def __init__(self):
        self.config = {
            "password_min_length": 8,
            "password_require_uppercase": True,
            "password_require_lowercase": True,
            "password_require_numbers": True,
            "password_require_symbols": True,
            "token_expiry_hours": 24,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "session_timeout_minutes": 60,
            "require_2fa": False,
            "encrypt_sensitive_fields": True,
            "audit_all_operations": True
        }
    
    def validate_password(self, password: str) -> List[str]:
        """Validate password against security policy"""
        errors = []
        
        if len(password) < self.config["password_min_length"]:
            errors.append(f"Password must be at least {self.config['password_min_length']} characters")
        
        if self.config["password_require_uppercase"] and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config["password_require_lowercase"] and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config["password_require_numbers"] and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.config["password_require_symbols"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one symbol")
        
        return errors
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


# Export all classes
__all__ = [
    "PasswordManager",
    "JWTManager",
    "RoleBasedAccessControl",
    "DataEncryption",
    "SecurityMiddleware",
    "AuditLog",
    "SecurityConfig"
]