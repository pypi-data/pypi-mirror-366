"""Real-time features for gdmongolite - WebSockets, Change Streams, Live Updates"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
import weakref

from fastapi import WebSocket, WebSocketDisconnect
from .core import Schema, DB
from .exceptions import GDMongoError


class ChangeStreamManager:
    """Manage MongoDB change streams for real-time updates"""
    
    def __init__(self, db: DB):
        self.db = db
        self.active_streams = {}
        self.subscribers = {}
    
    async def watch_collection(
        self, 
        schema: Schema, 
        callback: Callable,
        pipeline: List[Dict] = None,
        full_document: str = "updateLookup"
    ):
        """Watch a collection for changes"""
        collection = schema._get_collection("async")
        collection_name = schema._collection_name
        
        try:
            # Create change stream
            change_stream = collection.watch(
                pipeline=pipeline or [],
                full_document=full_document
            )
            
            self.active_streams[collection_name] = change_stream
            
            # Listen for changes
            async for change in change_stream:
                await callback(change)
                
        except Exception as e:
            raise GDMongoError(f"Failed to watch collection {collection_name}: {e}")
    
    async def watch_database(self, callback: Callable, pipeline: List[Dict] = None):
        """Watch entire database for changes"""
        try:
            db_instance = self.db._get_db("async")
            change_stream = db_instance.watch(pipeline=pipeline or [])
            
            async for change in change_stream:
                await callback(change)
                
        except Exception as e:
            raise GDMongoError(f"Failed to watch database: {e}")
    
    def stop_watching(self, collection_name: str = None):
        """Stop watching collection or all collections"""
        if collection_name:
            if collection_name in self.active_streams:
                self.active_streams[collection_name].close()
                del self.active_streams[collection_name]
        else:
            for stream in self.active_streams.values():
                stream.close()
            self.active_streams.clear()


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, room: str = "default", user_id: str = None):
        """Connect a WebSocket to a room"""
        await websocket.accept()
        
        if room not in self.active_connections:
            self.active_connections[room] = set()
        
        self.active_connections[room].add(websocket)
        self.connection_metadata[websocket] = {
            "room": room,
            "user_id": user_id,
            "connected_at": datetime.now()
        }
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket"""
        if websocket in self.connection_metadata:
            room = self.connection_metadata[websocket]["room"]
            if room in self.active_connections:
                self.active_connections[room].discard(websocket)
                if not self.active_connections[room]:
                    del self.active_connections[room]
            del self.connection_metadata[websocket]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
    
    async def send_to_room(self, message: str, room: str):
        """Send message to all WebSockets in a room"""
        if room in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[room]:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for websocket in disconnected:
                self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected WebSockets"""
        for room in self.active_connections:
            await self.send_to_room(message, room)
    
    def get_room_connections(self, room: str) -> int:
        """Get number of connections in a room"""
        return len(self.active_connections.get(room, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of connections"""
        return sum(len(connections) for connections in self.active_connections.values())


class LiveQuery:
    """Live query that updates in real-time"""
    
    def __init__(self, schema: Schema, filters: Dict, websocket_manager: WebSocketManager):
        self.schema = schema
        self.filters = filters
        self.websocket_manager = websocket_manager
        self.subscribers = set()
        self.last_results = []
        self.change_stream = None
    
    async def subscribe(self, websocket: WebSocket, room: str = None):
        """Subscribe to live query updates"""
        room = room or f"live_query_{self.schema._collection_name}"
        await self.websocket_manager.connect(websocket, room)
        self.subscribers.add(websocket)
        
        # Send initial results
        initial_results = await self.schema.find(**self.filters).to_list()
        await self.websocket_manager.send_personal_message(
            json.dumps({
                "type": "initial_data",
                "data": initial_results,
                "count": len(initial_results)
            }),
            websocket
        )
        
        # Start watching for changes if not already started
        if not self.change_stream:
            await self._start_watching()
    
    async def _start_watching(self):
        """Start watching for changes"""
        async def handle_change(change):
            # Check if change matches our filters
            if self._change_matches_filters(change):
                # Get updated results
                new_results = await self.schema.find(**self.filters).to_list()
                
                # Send update to all subscribers
                message = json.dumps({
                    "type": "data_update",
                    "change_type": change["operationType"],
                    "data": new_results,
                    "count": len(new_results),
                    "timestamp": datetime.now().isoformat()
                })
                
                for websocket in self.subscribers.copy():
                    try:
                        await websocket.send_text(message)
                    except:
                        self.subscribers.discard(websocket)
                
                self.last_results = new_results
        
        # Start change stream
        change_stream_manager = ChangeStreamManager(self.schema._db)
        await change_stream_manager.watch_collection(self.schema, handle_change)
    
    def _change_matches_filters(self, change) -> bool:
        """Check if a change matches our query filters"""
        # Simple implementation - in production, this would be more sophisticated
        return True
    
    def unsubscribe(self, websocket: WebSocket):
        """Unsubscribe from live query"""
        self.subscribers.discard(websocket)
        self.websocket_manager.disconnect(websocket)


class RealtimeAPI:
    """Real-time API endpoints for FastAPI integration"""
    
    def __init__(self, db: DB):
        self.db = db
        self.websocket_manager = WebSocketManager()
        self.change_stream_manager = ChangeStreamManager(db)
        self.live_queries = {}
    
    def add_realtime_routes(self, app, schemas: List[Schema]):
        """Add real-time routes to FastAPI app"""
        
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """General WebSocket endpoint"""
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_websocket_message(websocket, message)
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
        
        @app.websocket("/ws/live-query/{collection}")
        async def live_query_endpoint(websocket: WebSocket, collection: str):
            """Live query WebSocket endpoint"""
            # Find schema by collection name
            schema = None
            for s in schemas:
                if s._collection_name == collection:
                    schema = s
                    break
            
            if not schema:
                await websocket.close(code=4004, reason="Collection not found")
                return
            
            try:
                # Get query parameters from WebSocket
                await websocket.accept()
                query_data = await websocket.receive_text()
                filters = json.loads(query_data) if query_data else {}
                
                # Create live query
                live_query = LiveQuery(schema, filters, self.websocket_manager)
                await live_query.subscribe(websocket)
                
                # Keep connection alive
                while True:
                    await websocket.receive_text()
                    
            except WebSocketDisconnect:
                if websocket in live_query.subscribers:
                    live_query.unsubscribe(websocket)
        
        @app.get("/realtime/stats")
        async def realtime_stats():
            """Get real-time connection statistics"""
            return {
                "total_connections": self.websocket_manager.get_total_connections(),
                "rooms": {
                    room: len(connections) 
                    for room, connections in self.websocket_manager.active_connections.items()
                },
                "active_streams": len(self.change_stream_manager.active_streams)
            }
    
    async def _handle_websocket_message(self, websocket: WebSocket, message: Dict):
        """Handle incoming WebSocket messages"""
        msg_type = message.get("type")
        
        if msg_type == "join_room":
            room = message.get("room", "default")
            await self.websocket_manager.connect(websocket, room)
            
        elif msg_type == "send_to_room":
            room = message.get("room")
            text = message.get("message")
            if room and text:
                await self.websocket_manager.send_to_room(text, room)
        
        elif msg_type == "broadcast":
            text = message.get("message")
            if text:
                await self.websocket_manager.broadcast(text)


class NotificationSystem:
    """Advanced notification system"""
    
    def __init__(self, db: DB):
        self.db = db
        self.subscribers = {}
        self.notification_handlers = {}
    
    def subscribe(self, event: str, callback: Callable):
        """Subscribe to notifications"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)
    
    async def notify(self, event: str, data: Any):
        """Send notification to subscribers"""
        if event in self.subscribers:
            for callback in self.subscribers[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Notification callback error: {e}")
    
    def add_database_triggers(self, schema: Schema):
        """Add database triggers for automatic notifications"""
        original_insert = schema.insert
        original_update = schema.update
        original_delete = schema.delete
        
        async def insert_with_notification(*args, **kwargs):
            result = await original_insert(*args, **kwargs)
            if result.success:
                await self.notify(f"{schema._collection_name}_inserted", {
                    "collection": schema._collection_name,
                    "data": result.data,
                    "timestamp": datetime.now()
                })
            return result
        
        async def update_with_notification(*args, **kwargs):
            result = await original_update(*args, **kwargs)
            if result.success:
                await self.notify(f"{schema._collection_name}_updated", {
                    "collection": schema._collection_name,
                    "count": result.count,
                    "timestamp": datetime.now()
                })
            return result
        
        async def delete_with_notification(*args, **kwargs):
            result = await original_delete(*args, **kwargs)
            if result.success:
                await self.notify(f"{schema._collection_name}_deleted", {
                    "collection": schema._collection_name,
                    "count": result.count,
                    "timestamp": datetime.now()
                })
            return result
        
        schema.insert = insert_with_notification
        schema.update = update_with_notification
        schema.delete = delete_with_notification


# Export all classes
__all__ = [
    "ChangeStreamManager",
    "WebSocketManager", 
    "LiveQuery",
    "RealtimeAPI",
    "NotificationSystem"
]