"""Advanced monitoring and observability for gdmongolite"""

import time
import asyncio
import psutil
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from .core import DB, Schema
from .exceptions import GDMongoError


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    collection: str
    operation: str
    duration_ms: float
    documents_examined: int
    documents_returned: int
    index_used: bool
    timestamp: datetime
    query_hash: str
    user_id: Optional[str] = None


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io_mb: float
    timestamp: datetime


class MetricsCollector:
    """Collect and store performance metrics"""
    
    def __init__(self, db: DB):
        self.db = db
        self.query_metrics = []
        self.system_metrics = []
        self.alerts = []
        self.thresholds = {
            "slow_query_ms": 1000,
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_usage_percent": 90
        }
        self.collection_stats = {}
        self._monitoring_active = False
    
    async def record_query_metric(self, metric: QueryMetrics):
        """Record query performance metric"""
        self.query_metrics.append(metric)
        
        # Check for slow query alert
        if metric.duration_ms > self.thresholds["slow_query_ms"]:
            await self._trigger_alert(
                "slow_query",
                f"Slow query detected: {metric.operation} on {metric.collection} took {metric.duration_ms}ms"
            )
        
        # Update collection stats
        if metric.collection not in self.collection_stats:
            self.collection_stats[metric.collection] = {
                "total_queries": 0,
                "total_duration": 0,
                "slow_queries": 0,
                "avg_duration": 0
            }
        
        stats = self.collection_stats[metric.collection]
        stats["total_queries"] += 1
        stats["total_duration"] += metric.duration_ms
        stats["avg_duration"] = stats["total_duration"] / stats["total_queries"]
        
        if metric.duration_ms > self.thresholds["slow_query_ms"]:
            stats["slow_queries"] += 1
        
        # Keep only recent metrics (last 1000)
        if len(self.query_metrics) > 1000:
            self.query_metrics = self.query_metrics[-1000:]
    
    async def record_system_metric(self, metric: SystemMetrics):
        """Record system performance metric"""
        self.system_metrics.append(metric)
        
        # Check for system alerts
        if metric.cpu_percent > self.thresholds["cpu_percent"]:
            await self._trigger_alert(
                "high_cpu",
                f"High CPU usage: {metric.cpu_percent}%"
            )
        
        if metric.memory_percent > self.thresholds["memory_percent"]:
            await self._trigger_alert(
                "high_memory",
                f"High memory usage: {metric.memory_percent}%"
            )
        
        if metric.disk_usage_percent > self.thresholds["disk_usage_percent"]:
            await self._trigger_alert(
                "high_disk",
                f"High disk usage: {metric.disk_usage_percent}%"
            )
        
        # Keep only recent metrics (last 1000)
        if len(self.system_metrics) > 1000:
            self.system_metrics = self.system_metrics[-1000:]
    
    async def _trigger_alert(self, alert_type: str, message: str):
        """Trigger performance alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now(),
            "resolved": False
        }
        self.alerts.append(alert)
        
        # Keep only recent alerts (last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        print(f"ALERT [{alert_type}]: {message}")
    
    def get_query_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get query statistics for time period"""
        since = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.query_metrics if m.timestamp >= since]
        
        if not recent_metrics:
            return {"total_queries": 0}
        
        total_queries = len(recent_metrics)
        total_duration = sum(m.duration_ms for m in recent_metrics)
        slow_queries = sum(1 for m in recent_metrics if m.duration_ms > self.thresholds["slow_query_ms"])
        
        # Group by collection
        by_collection = {}
        for metric in recent_metrics:
            if metric.collection not in by_collection:
                by_collection[metric.collection] = []
            by_collection[metric.collection].append(metric)
        
        collection_stats = {}
        for collection, metrics in by_collection.items():
            collection_stats[collection] = {
                "query_count": len(metrics),
                "avg_duration": sum(m.duration_ms for m in metrics) / len(metrics),
                "slow_queries": sum(1 for m in metrics if m.duration_ms > self.thresholds["slow_query_ms"])
            }
        
        return {
            "total_queries": total_queries,
            "avg_duration": total_duration / total_queries,
            "slow_queries": slow_queries,
            "slow_query_rate": slow_queries / total_queries,
            "by_collection": collection_stats
        }
    
    def get_system_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get system statistics for time period"""
        since = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.system_metrics if m.timestamp >= since]
        
        if not recent_metrics:
            return {}
        
        return {
            "avg_cpu": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "max_cpu": max(m.cpu_percent for m in recent_metrics),
            "avg_memory": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            "max_memory": max(m.memory_percent for m in recent_metrics),
            "avg_disk": sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
            "samples": len(recent_metrics)
        }
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts"""
        return [alert for alert in self.alerts if not alert["resolved"]]
    
    async def start_system_monitoring(self, interval_seconds: int = 60):
        """Start background system monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        
        async def monitor_loop():
            while self._monitoring_active:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    network = psutil.net_io_counters()
                    
                    metric = SystemMetrics(
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_used_mb=memory.used / (1024 * 1024),
                        disk_usage_percent=disk.percent,
                        network_io_mb=(network.bytes_sent + network.bytes_recv) / (1024 * 1024),
                        timestamp=datetime.now()
                    )
                    
                    await self.record_system_metric(metric)
                    
                except Exception as e:
                    print(f"System monitoring error: {e}")
                
                await asyncio.sleep(interval_seconds)
        
        asyncio.create_task(monitor_loop())
    
    def stop_system_monitoring(self):
        """Stop background system monitoring"""
        self._monitoring_active = False


class HealthChecker:
    """Health check system"""
    
    def __init__(self, db: DB):
        self.db = db
        self.health_checks = {}
        self.last_results = {}
    
    def register_check(self, name: str, check_func: Callable, critical: bool = False):
        """Register health check"""
        self.health_checks[name] = {
            "func": check_func,
            "critical": critical
        }
    
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Run specific health check"""
        if name not in self.health_checks:
            return {"status": "error", "message": "Check not found"}
        
        check = self.health_checks[name]
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(check["func"]):
                result = await check["func"]()
            else:
                result = check["func"]()
            
            duration = (time.time() - start_time) * 1000
            
            check_result = {
                "status": "healthy" if result else "unhealthy",
                "duration_ms": duration,
                "timestamp": datetime.now().isoformat(),
                "critical": check["critical"]
            }
            
            if isinstance(result, dict):
                check_result.update(result)
            
            self.last_results[name] = check_result
            return check_result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            check_result = {
                "status": "error",
                "error": str(e),
                "duration_ms": duration,
                "timestamp": datetime.now().isoformat(),
                "critical": check["critical"]
            }
            
            self.last_results[name] = check_result
            return check_result
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = "healthy"
        
        for name in self.health_checks:
            result = await self.run_check(name)
            results[name] = result
            
            if result["status"] == "error" or result["status"] == "unhealthy":
                if self.health_checks[name]["critical"]:
                    overall_status = "critical"
                elif overall_status == "healthy":
                    overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def setup_default_checks(self):
        """Setup default health checks"""
        
        async def database_check():
            """Check database connectivity"""
            try:
                db_instance = self.db._get_db("async")
                await db_instance.command("ping")
                return {"status": "healthy", "message": "Database connected"}
            except Exception as e:
                return {"status": "unhealthy", "message": f"Database error: {e}"}
        
        def memory_check():
            """Check memory usage"""
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return {"status": "unhealthy", "memory_percent": memory.percent}
            elif memory.percent > 80:
                return {"status": "degraded", "memory_percent": memory.percent}
            else:
                return {"status": "healthy", "memory_percent": memory.percent}
        
        def disk_check():
            """Check disk usage"""
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                return {"status": "unhealthy", "disk_percent": disk.percent}
            elif disk.percent > 85:
                return {"status": "degraded", "disk_percent": disk.percent}
            else:
                return {"status": "healthy", "disk_percent": disk.percent}
        
        self.register_check("database", database_check, critical=True)
        self.register_check("memory", memory_check, critical=False)
        self.register_check("disk", disk_check, critical=False)


class PerformanceProfiler:
    """Profile database operations"""
    
    def __init__(self, db: DB):
        self.db = db
        self.profiles = {}
        self.active_profiles = {}
    
    async def start_profiling(self, name: str):
        """Start profiling session"""
        self.active_profiles[name] = {
            "start_time": time.time(),
            "operations": [],
            "queries": []
        }
    
    async def record_operation(self, profile_name: str, operation: str, duration: float, details: Dict = None):
        """Record operation in profile"""
        if profile_name in self.active_profiles:
            self.active_profiles[profile_name]["operations"].append({
                "operation": operation,
                "duration": duration,
                "details": details or {},
                "timestamp": time.time()
            })
    
    async def stop_profiling(self, name: str) -> Dict[str, Any]:
        """Stop profiling and get results"""
        if name not in self.active_profiles:
            return {}
        
        profile = self.active_profiles[name]
        total_time = time.time() - profile["start_time"]
        
        result = {
            "name": name,
            "total_time": total_time,
            "operations": profile["operations"],
            "operation_count": len(profile["operations"]),
            "avg_operation_time": sum(op["duration"] for op in profile["operations"]) / len(profile["operations"]) if profile["operations"] else 0
        }
        
        self.profiles[name] = result
        del self.active_profiles[name]
        
        return result
    
    def get_profile_summary(self, name: str) -> Dict[str, Any]:
        """Get profile summary"""
        if name not in self.profiles:
            return {}
        
        profile = self.profiles[name]
        operations = profile["operations"]
        
        # Group by operation type
        by_operation = {}
        for op in operations:
            op_type = op["operation"]
            if op_type not in by_operation:
                by_operation[op_type] = []
            by_operation[op_type].append(op)
        
        operation_stats = {}
        for op_type, ops in by_operation.items():
            operation_stats[op_type] = {
                "count": len(ops),
                "total_time": sum(op["duration"] for op in ops),
                "avg_time": sum(op["duration"] for op in ops) / len(ops),
                "min_time": min(op["duration"] for op in ops),
                "max_time": max(op["duration"] for op in ops)
            }
        
        return {
            "name": name,
            "total_time": profile["total_time"],
            "operation_count": profile["operation_count"],
            "by_operation": operation_stats
        }


class MonitoringDashboard:
    """Simple monitoring dashboard data"""
    
    def __init__(self, metrics_collector: MetricsCollector, health_checker: HealthChecker):
        self.metrics = metrics_collector
        self.health = health_checker
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data"""
        health_status = await self.health.run_all_checks()
        query_stats = self.metrics.get_query_stats(hours=24)
        system_stats = self.metrics.get_system_stats(hours=24)
        active_alerts = self.metrics.get_active_alerts()
        
        return {
            "health": health_status,
            "queries": query_stats,
            "system": system_stats,
            "alerts": active_alerts,
            "collection_stats": self.metrics.collection_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        data = {
            "query_metrics": [asdict(m) for m in self.metrics.query_metrics],
            "system_metrics": [asdict(m) for m in self.system_metrics],
            "alerts": self.metrics.alerts,
            "collection_stats": self.metrics.collection_stats
        }
        
        if format == "json":
            return json.dumps(data, default=str, indent=2)
        else:
            return str(data)


# Integration with gdmongolite core
def add_monitoring_to_db(db: DB):
    """Add monitoring capabilities to DB instance"""
    db.metrics_collector = MetricsCollector(db)
    db.health_checker = HealthChecker(db)
    db.profiler = PerformanceProfiler(db)
    
    # Setup default health checks
    db.health_checker.setup_default_checks()
    
    # Create dashboard
    db.dashboard = MonitoringDashboard(db.metrics_collector, db.health_checker)
    
    return db


# Export all classes
__all__ = [
    "QueryMetrics",
    "SystemMetrics", 
    "MetricsCollector",
    "HealthChecker",
    "PerformanceProfiler",
    "MonitoringDashboard",
    "add_monitoring_to_db"
]