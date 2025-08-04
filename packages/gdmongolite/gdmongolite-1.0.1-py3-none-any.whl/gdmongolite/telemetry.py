"""Telemetry and hooks system for gdmongolite"""

import asyncio
from typing import Dict, List, Callable, Any
from datetime import datetime
import functools
import time

class TelemetryManager:
    """Manage telemetry hooks and events"""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {
            # Query events
            'pre_query': [],
            'post_query': [],
            
            # Insert events
            'pre_insert': [],
            'post_insert': [],
            
            # Update events
            'pre_update': [],
            'post_update': [],
            
            # Delete events
            'pre_delete': [],
            'post_delete': [],
            
            # Connection events
            'connection_created': [],
            'connection_closed': [],
            
            # Error events
            'error': [],
            
            # Performance events
            'slow_query': [],
            'performance': [],
        }
        
        # Configuration
        self.slow_query_threshold = 1000  # milliseconds
        self.enabled = True
        
        # Initialize performance monitor
        self.performance_monitor = PerformanceMonitor(self)
    
    def on(self, event: str):
        """Decorator to register event hooks
        
        Usage:
            @db.on('pre_query')
            def log_query(collection, query, options):
                print(f"Querying {collection}: {query}")
        """
        def decorator(func: Callable):
            if event in self.hooks:
                self.hooks[event].append(func)
            else:
                raise ValueError(f"Unknown event: {event}")
            return func
        return decorator
    
    def register_hook(self, event: str, func: Callable):
        """Programmatically register a hook"""
        if event in self.hooks:
            self.hooks[event].append(func)
        else:
            raise ValueError(f"Unknown event: {event}")
    
    def remove_hook(self, event: str, func: Callable):
        """Remove a registered hook"""
        if event in self.hooks and func in self.hooks[event]:
            self.hooks[event].remove(func)
    
    def emit(self, event: str, *args, **kwargs):
        """Emit an event to all registered hooks"""
        if not self.enabled:
            return
        
        if event in self.hooks:
            for hook in self.hooks[event]:
                try:
                    hook(*args, **kwargs)
                except Exception as e:
                    # Don't let hook errors break the main operation
                    self.emit('error', f"Hook error in {event}: {e}")
    
    def clear_hooks(self, event: str = None):
        """Clear hooks for an event or all events"""
        if event:
            if event in self.hooks:
                self.hooks[event].clear()
        else:
            for hook_list in self.hooks.values():
                hook_list.clear()
    
    def enable(self):
        """Enable telemetry"""
        self.enabled = True
    
    def disable(self):
        """Disable telemetry"""
        self.enabled = False
    
    def set_slow_query_threshold(self, threshold_ms: int):
        """Set slow query threshold in milliseconds"""
        self.slow_query_threshold = threshold_ms

def with_telemetry(event_prefix: str):
    """Decorator to add telemetry to methods"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(cls, *args, **kwargs):
            if hasattr(cls, '_db') and cls._db.telemetry.enabled:
                telemetry = cls._db.telemetry
                
                # Pre-event
                start_time = time.time()
                telemetry.emit(f'pre_{event_prefix}', cls._collection_name, args, kwargs)
                
                try:
                    result = await func(cls, *args, **kwargs)
                    
                    # Post-event
                    duration = (time.time() - start_time) * 1000
                    telemetry.emit(f'post_{event_prefix}', cls._collection_name, result, duration)
                    
                    # Check for slow operations
                    if duration > telemetry.slow_query_threshold:
                        telemetry.emit('slow_query', cls._collection_name, args, kwargs, duration)
                    
                    return result
                
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    telemetry.emit('error', cls._collection_name, str(e), duration)
                    raise
            else:
                return await func(cls, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(cls, *args, **kwargs):
            if hasattr(cls, '_db') and cls._db.telemetry.enabled:
                telemetry = cls._db.telemetry
                
                # Pre-event
                start_time = time.time()
                telemetry.emit(f'pre_{event_prefix}', cls._collection_name, args, kwargs)
                
                try:
                    result = func(cls, *args, **kwargs)
                    
                    # Post-event
                    duration = (time.time() - start_time) * 1000
                    telemetry.emit(f'post_{event_prefix}', cls._collection_name, result, duration)
                    
                    # Check for slow operations
                    if duration > telemetry.slow_query_threshold:
                        telemetry.emit('slow_query', cls._collection_name, args, kwargs, duration)
                    
                    return result
                
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    telemetry.emit('error', cls._collection_name, str(e), duration)
                    raise
            else:
                return func(cls, *args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class PerformanceMonitor:
    """Built-in performance monitoring"""
    
    def __init__(self, telemetry_manager: TelemetryManager):
        self.telemetry = telemetry_manager
        self.stats = {
            'queries': 0,
            'inserts': 0,
            'updates': 0,
            'deletes': 0,
            'total_time': 0,
            'slow_queries': 0,
            'errors': 0
        }
        
        # Register built-in hooks
        self._register_hooks()
    
    def _register_hooks(self):
        """Register performance monitoring hooks"""
        
        @self.telemetry.on('post_query')
        def track_query(collection, result, duration):
            self.stats['queries'] += 1
            self.stats['total_time'] += duration
        
        @self.telemetry.on('post_insert')
        def track_insert(collection, result, duration):
            self.stats['inserts'] += 1
            self.stats['total_time'] += duration
        
        @self.telemetry.on('post_update')
        def track_update(collection, result, duration):
            self.stats['updates'] += 1
            self.stats['total_time'] += duration
        
        @self.telemetry.on('post_delete')
        def track_delete(collection, result, duration):
            self.stats['deletes'] += 1
            self.stats['total_time'] += duration
        
        @self.telemetry.on('slow_query')
        def track_slow_query(collection, args, kwargs, duration):
            self.stats['slow_queries'] += 1
        
        @self.telemetry.on('error')
        def track_error(collection, error, duration):
            self.stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_ops = sum([
            self.stats['queries'],
            self.stats['inserts'], 
            self.stats['updates'],
            self.stats['deletes']
        ])
        
        return {
            **self.stats,
            'total_operations': total_ops,
            'average_time': self.stats['total_time'] / total_ops if total_ops > 0 else 0,
            'error_rate': self.stats['errors'] / total_ops if total_ops > 0 else 0,
            'slow_query_rate': self.stats['slow_queries'] / total_ops if total_ops > 0 else 0
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        for key in self.stats:
            self.stats[key] = 0
    
    def print_stats(self):
        """Print formatted performance statistics"""
        stats = self.get_stats()
        
        print("=== gdmongolite Performance Stats ===")
        print(f"Total Operations: {stats['total_operations']}")
        print(f"  - Queries: {stats['queries']}")
        print(f"  - Inserts: {stats['inserts']}")
        print(f"  - Updates: {stats['updates']}")
        print(f"  - Deletes: {stats['deletes']}")
        print(f"Average Time: {stats['average_time']:.2f}ms")
        print(f"Slow Queries: {stats['slow_queries']} ({stats['slow_query_rate']:.1%})")
        print(f"Errors: {stats['errors']} ({stats['error_rate']:.1%})")
        print("=====================================")

# Built-in telemetry hooks for common use cases
class BuiltinHooks:
    """Collection of built-in telemetry hooks"""
    
    @staticmethod
    def console_logger():
        """Simple console logging hook"""
        def log_operation(event, collection, *args):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {event.upper()}: {collection}")
        return log_operation
    
    @staticmethod
    def json_logger(file_path: str):
        """JSON file logging hook"""
        import json
        
        def log_to_json(event, collection, *args):
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event': event,
                'collection': collection,
                'args': str(args)
            }
            
            try:
                with open(file_path, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception:
                pass  # Don't break on logging errors
        
        return log_to_json
    
    @staticmethod
    def metrics_collector():
        """Collect metrics for external systems"""
        metrics = {'operations': 0, 'errors': 0}
        
        def collect_metrics(event, *args):
            if event.startswith('post_'):
                metrics['operations'] += 1
            elif event == 'error':
                metrics['errors'] += 1
        
        collect_metrics.get_metrics = lambda: metrics.copy()
        collect_metrics.reset_metrics = lambda: metrics.update({'operations': 0, 'errors': 0})
        
        return collect_metrics