"""
WebSocket manager for real-time communication
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import threading
import time
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
import eventlet
from caching.redis_cache import get_cache

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

class WebSocketManager:
    """
    WebSocket manager for real-time communication
    """

    def __init__(self):
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.rooms: Dict[str, List[str]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.cache = get_cache()
        self.monitoring_thread = None
        self.is_monitoring = False

    def init_app(self, app):
        """
        Initialize WebSocket manager with Flask app

        Args:
            app: Flask application instance
        """
        socketio.init_app(app)

        # Register SocketIO event handlers
        self._register_socketio_handlers()

        # Start monitoring thread
        self.start_monitoring()

    def _register_socketio_handlers(self):
        """Register SocketIO event handlers"""

        @socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.connected_clients[client_id] = {
                'connected_at': datetime.now(),
                'rooms': [],
                'last_activity': datetime.now()
            }
            print(f"✅ Client connected: {client_id}")
            emit('connected', {'client_id': client_id, 'timestamp': datetime.now().isoformat()})

        @socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            if client_id in self.connected_clients:
                # Leave all rooms
                for room in self.connected_clients[client_id]['rooms']:
                    leave_room(room)
                    if room in self.rooms and client_id in self.rooms[room]:
                        self.rooms[room].remove(client_id)

                # Remove client
                del self.connected_clients[client_id]
                print(f"❌ Client disconnected: {client_id}")

        @socketio.on('join_room')
        def handle_join_room(data):
            """Handle room joining"""
            client_id = request.sid
            room = data.get('room')
            if room and client_id in self.connected_clients:
                join_room(room)
                self.connected_clients[client_id]['rooms'].append(room)
                if room not in self.rooms:
                    self.rooms[room] = []
                if client_id not in self.rooms[room]:
                    self.rooms[room].append(client_id)

                emit('room_joined', {'room': room, 'timestamp': datetime.now().isoformat()})
                print(f"📱 Client {client_id} joined room: {room}")

        @socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle room leaving"""
            client_id = request.sid
            room = data.get('room')
            if room and client_id in self.connected_clients:
                leave_room(room)
                if room in self.connected_clients[client_id]['rooms']:
                    self.connected_clients[client_id]['rooms'].remove(room)
                if room in self.rooms and client_id in self.rooms[room]:
                    self.rooms[room].remove(client_id)

                emit('room_left', {'room': room, 'timestamp': datetime.now().isoformat()})
                print(f"📱 Client {client_id} left room: {room}")

        @socketio.on('subscribe')
        def handle_subscribe(data):
            """Handle event subscription"""
            client_id = request.sid
            event = data.get('event')
            if event:
                if event not in self.event_handlers:
                    self.event_handlers[event] = []
                if client_id not in [handler['client_id'] for handler in self.event_handlers[event]]:
                    self.event_handlers[event].append({
                        'client_id': client_id,
                        'callback': None
                    })
                emit('subscribed', {'event': event, 'timestamp': datetime.now().isoformat()})
                print(f"📡 Client {client_id} subscribed to event: {event}")

        @socketio.on('unsubscribe')
        def handle_unsubscribe(data):
            """Handle event unsubscription"""
            client_id = request.sid
            event = data.get('event')
            if event and event in self.event_handlers:
                self.event_handlers[event] = [
                    handler for handler in self.event_handlers[event]
                    if handler['client_id'] != client_id
                ]
                emit('unsubscribed', {'event': event, 'timestamp': datetime.now().isoformat()})
                print(f"📡 Client {client_id} unsubscribed from event: {event}")

    def emit_to_client(self, client_id: str, event: str, data: Any):
        """
        Emit event to specific client

        Args:
            client_id: Client socket ID
            event: Event name
            data: Event data
        """
        if client_id in self.connected_clients:
            socketio.emit(event, data, to=client_id)

    def emit_to_room(self, room: str, event: str, data: Any):
        """
        Emit event to all clients in a room

        Args:
            room: Room name
            event: Event name
            data: Event data
        """
        socketio.emit(event, data, to=room)

    def broadcast(self, event: str, data: Any):
        """
        Broadcast event to all connected clients

        Args:
            event: Event name
            data: Event data
        """
        socketio.emit(event, data)

    def register_event_handler(self, event: str, handler: Callable):
        """
        Register event handler

        Args:
            event: Event name
            handler: Handler function
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append({
            'client_id': None,
            'callback': handler
        })

    def trigger_event(self, event: str, data: Any):
        """
        Trigger custom event

        Args:
            event: Event name
            data: Event data
        """
        # Call registered handlers
        if event in self.event_handlers:
            for handler_info in self.event_handlers[event]:
                if handler_info['callback']:
                    try:
                        handler_info['callback'](data)
                    except Exception as e:
                        print(f"❌ Event handler error for {event}: {e}")

        # Emit to subscribed clients
        self.broadcast(event, data)

    def start_monitoring(self):
        """Start real-time monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            print("📊 Real-time monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring thread"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
            print("📊 Real-time monitoring stopped")

    def _monitoring_loop(self):
        """Monitoring loop for real-time updates"""
        while self.is_monitoring:
            try:
                # Send system health updates
                health_data = self._get_system_health()
                self.emit_to_room('monitoring', 'system_health', health_data)

                # Send GPU status updates
                gpu_data = self._get_gpu_status()
                self.emit_to_room('gpu_monitoring', 'gpu_status', gpu_data)

                # Send revenue updates
                revenue_data = self._get_revenue_updates()
                self.emit_to_room('revenue_monitoring', 'revenue_update', revenue_data)

                # Clean up inactive clients
                self._cleanup_inactive_clients()

                time.sleep(30)  # Update every 30 seconds

            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(5)

    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'connected_clients': len(self.connected_clients),
            'active_rooms': len(self.rooms),
            'cache_status': self.cache.is_connected(),
            'memory_usage': 'N/A',  # Would need psutil for actual memory usage
            'cpu_usage': 'N/A'      # Would need psutil for actual CPU usage
        }

    def _get_gpu_status(self) -> Dict[str, Any]:
        """Get GPU status data"""
        # This would integrate with NVIDIA integration
        return {
            'timestamp': datetime.now().isoformat(),
            'gpu_count': 0,  # Would be populated from NVIDIA integration
            'total_memory': '0 GB',
            'utilization': 0
        }

    def _get_revenue_updates(self) -> Dict[str, Any]:
        """Get revenue update data"""
        # This would integrate with revenue tracking
        return {
            'timestamp': datetime.now().isoformat(),
            'total_revenue': 0.0,
            'recent_transactions': [],
            'growth_rate': 0.0
        }

    def _cleanup_inactive_clients(self):
        """Clean up inactive clients"""
        current_time = datetime.now()
        inactive_clients = []

        for client_id, client_info in self.connected_clients.items():
            # Consider client inactive if no activity for 5 minutes
            if (current_time - client_info['last_activity']).seconds > 300:
                inactive_clients.append(client_id)

        for client_id in inactive_clients:
            print(f"🧹 Cleaning up inactive client: {client_id}")
            # Leave all rooms
            for room in self.connected_clients[client_id]['rooms']:
                if room in self.rooms and client_id in self.rooms[room]:
                    self.rooms[room].remove(client_id)
            del self.connected_clients[client_id]

    def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get client information

        Args:
            client_id: Client socket ID

        Returns:
            Client information or None if not found
        """
        return self.connected_clients.get(client_id)

    def get_room_clients(self, room: str) -> List[str]:
        """
        Get all clients in a room

        Args:
            room: Room name

        Returns:
            List of client IDs in the room
        """
        return self.rooms.get(room, [])

    def get_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket manager statistics

        Returns:
            Statistics dictionary
        """
        return {
            'connected_clients': len(self.connected_clients),
            'active_rooms': len(self.rooms),
            'event_handlers': {k: len(v) for k, v in self.event_handlers.items()}
        }
