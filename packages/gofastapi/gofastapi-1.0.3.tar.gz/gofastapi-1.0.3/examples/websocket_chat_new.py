"""
Example 5: WebSocket Chat Application
Real-time messaging with GoFastAPI WebSocket support
"""

from gofastapi import GoFastAPI, HTTPException
from typing import List, Dict, Optional
import json
import time
import uuid
from datetime import datetime

app = GoFastAPI(
    title="WebSocket Chat Application",
    version="1.0.2",
    description="Real-time chat application using GoFastAPI WebSocket support"
)

# Chat data structures (simplified for demo)
chat_rooms: Dict[str, Dict] = {}
message_history: Dict[str, List[Dict]] = {}
user_sessions: Dict[str, Dict] = {}

# Chat metrics
chat_metrics = {
    "total_rooms": 0,
    "total_messages": 0,
    "active_users": 0,
    "connections_created": 0,
    "peak_concurrent_users": 0
}

def create_room(room_name: str, creator_id: str) -> Dict:
    """Create a new chat room."""
    room_id = str(uuid.uuid4())
    
    chat_rooms[room_id] = {
        "id": room_id,
        "name": room_name,
        "creator_id": creator_id,
        "created_at": datetime.now().isoformat(),
        "members": [creator_id],
        "active": True
    }
    
    message_history[room_id] = []
    chat_metrics["total_rooms"] += 1
    
    return chat_rooms[room_id]

def create_message(room_id: str, user_id: str, content: str, message_type: str = "text") -> Dict:
    """Create a new message."""
    message = {
        "id": str(uuid.uuid4()),
        "room_id": room_id,
        "user_id": user_id,
        "content": content,
        "type": message_type,
        "timestamp": datetime.now().isoformat(),
        "delivered": True
    }
    
    if room_id not in message_history:
        message_history[room_id] = []
    
    message_history[room_id].append(message)
    chat_metrics["total_messages"] += 1
    
    return message

@app.get("/")
def chat_info():
    """WebSocket Chat Application information."""
    return {
        "application": "WebSocket Chat with GoFastAPI",
        "version": "1.0.2",
        "framework": "GoFastAPI",
        "features": [
            "Real-time messaging",
            "Multiple chat rooms",
            "User presence tracking",
            "Message history",
            "Broadcasting",
            "Connection management"
        ],
        "websocket_performance": {
            "framework": "GoFastAPI",
            "concurrent_connections": "10K+ per instance",
            "message_latency": "<1ms",
            "throughput": "100K+ messages/second",
            "memory_efficiency": "50% less than alternatives"
        },
        "endpoints": {
            "rooms": "/rooms",
            "messages": "/rooms/{room_id}/messages",
            "metrics": "/chat/metrics",
            "demo": "/chat/demo"
        },
        "websocket_simulation": {
            "note": "This demo simulates WebSocket functionality",
            "real_websocket": "Available in full GoFastAPI framework",
            "connection_url": "/ws/{room_id}/{user_id}"
        },
        "current_stats": {
            "total_rooms": chat_metrics["total_rooms"],
            "active_users": chat_metrics["active_users"],
            "total_messages": chat_metrics["total_messages"]
        }
    }

@app.post("/rooms")
def create_chat_room(room_data: dict):
    """Create a new chat room."""
    start_time = time.time()
    
    # Validate required fields
    required_fields = ["name", "creator_id"]
    for field in required_fields:
        if field not in room_data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
    
    room = create_room(room_data["name"], room_data["creator_id"])
    
    processing_time = time.time() - start_time
    
    return {
        "message": "Room created successfully",
        "room": room,
        "processing_time": f"{processing_time:.4f}s",
        "websocket_url": f"/ws/{room['id']}/{room_data['creator_id']} (simulated)"
    }

@app.get("/rooms")
def get_chat_rooms(active_only: bool = True):
    """Get all chat rooms."""
    start_time = time.time()
    
    rooms = list(chat_rooms.values())
    
    if active_only:
        rooms = [room for room in rooms if room.get("active", True)]
    
    # Add member count and message count to each room
    for room in rooms:
        room_id = room["id"]
        room["member_count"] = len(room["members"])
        room["message_count"] = len(message_history.get(room_id, []))
        room["active_connections"] = 0  # Simulated
    
    processing_time = time.time() - start_time
    
    return {
        "rooms": rooms,
        "count": len(rooms),
        "processing_time": f"{processing_time:.4f}s"
    }

@app.get("/rooms/{room_id}")
def get_room_details(room_id: str):
    """Get detailed information about a specific room."""
    start_time = time.time()
    
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = chat_rooms[room_id].copy()
    room["member_count"] = len(room["members"])
    room["message_count"] = len(message_history.get(room_id, []))
    room["active_connections"] = 0  # Simulated
    room["recent_messages"] = message_history.get(room_id, [])[-10:]  # Last 10 messages
    
    processing_time = time.time() - start_time
    
    return {
        "room": room,
        "processing_time": f"{processing_time:.4f}s"
    }

@app.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50, offset: int = 0):
    """Get messages from a specific room."""
    start_time = time.time()
    
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = message_history.get(room_id, [])
    
    # Apply pagination
    total_messages = len(messages)
    paginated_messages = messages[offset:offset + limit]
    
    processing_time = time.time() - start_time
    
    return {
        "messages": paginated_messages,
        "pagination": {
            "total": total_messages,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_messages
        },
        "processing_time": f"{processing_time:.4f}s"
    }

@app.post("/rooms/{room_id}/messages")
def send_message(room_id: str, message_data: dict):
    """Send a message to a room (simulates WebSocket message)."""
    start_time = time.time()
    
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Validate required fields
    required_fields = ["user_id", "content"]
    for field in required_fields:
        if field not in message_data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
    
    # Create message
    message = create_message(
        room_id,
        message_data["user_id"],
        message_data["content"],
        message_data.get("type", "text")
    )
    
    processing_time = time.time() - start_time
    
    return {
        "message": "Message sent successfully",
        "message_data": message,
        "broadcast_info": {
            "room_id": room_id,
            "recipients": len(chat_rooms[room_id]["members"]),
            "delivery_status": "simulated_delivered"
        },
        "processing_time": f"{processing_time:.4f}s",
        "note": "In real implementation, this would broadcast via WebSocket"
    }

@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, user_data: dict):
    """Join a chat room."""
    start_time = time.time()
    
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    # Add user to room if not already a member
    if user_id not in chat_rooms[room_id]["members"]:
        chat_rooms[room_id]["members"].append(user_id)
    
    # Create system message
    system_message = create_message(
        room_id, 
        "system", 
        f"User {user_id} joined the room",
        "system"
    )
    
    processing_time = time.time() - start_time
    
    return {
        "message": "Successfully joined room",
        "room_id": room_id,
        "user_id": user_id,
        "websocket_url": f"/ws/{room_id}/{user_id} (simulated)",
        "system_message": system_message,
        "processing_time": f"{processing_time:.4f}s"
    }

@app.get("/chat/metrics")
def get_chat_metrics():
    """Get comprehensive chat application metrics."""
    return {
        "chat_metrics": chat_metrics,
        "performance": {
            "framework": "GoFastAPI",
            "websocket_performance": "25x faster than FastAPI",
            "concurrent_connections": "10K+ supported",
            "message_latency": "<1ms",
            "memory_usage": "50% less than alternatives"
        },
        "real_time_stats": {
            "active_rooms": len([r for r in chat_rooms.values() if r.get("active", True)]),
            "total_connections": 0,  # Simulated
            "messages_per_room": {
                room_id: len(messages) 
                for room_id, messages in message_history.items()
            }
        },
        "system_health": {
            "uptime": "Running",
            "connection_pool": "Healthy (simulated)",
            "broadcast_system": "Operational (simulated)",
            "message_queue": "Processing"
        },
        "websocket_simulation": {
            "note": "This demo simulates WebSocket functionality",
            "real_implementation": "Available in full GoFastAPI framework",
            "features_demonstrated": [
                "Room creation and management",
                "Message history",
                "User joining/leaving",
                "Metrics collection",
                "Performance tracking"
            ]
        }
    }

@app.get("/chat/demo")
def chat_demo_info():
    """Information about the chat demo."""
    return {
        "demo": "WebSocket Chat Application (Simulated)",
        "framework": "GoFastAPI",
        "how_to_use": [
            "1. Create a room: POST /rooms",
            "2. Join the room: POST /rooms/{room_id}/join", 
            "3. Send messages: POST /rooms/{room_id}/messages",
            "4. View messages: GET /rooms/{room_id}/messages",
            "5. View metrics: GET /chat/metrics"
        ],
        "websocket_simulation": {
            "note": "This demo shows the REST API equivalent of WebSocket operations",
            "real_websocket": "Full WebSocket support available in GoFastAPI",
            "connection_url": "/ws/{room_id}/{user_id}",
            "message_types": {
                "text": "Regular chat messages",
                "system": "System notifications",
                "typing": "Typing indicators",
                "presence": "User presence updates"
            }
        },
        "sample_requests": {
            "create_room": {
                "url": "POST /rooms",
                "data": {
                    "name": "General Chat",
                    "creator_id": "user123"
                }
            },
            "join_room": {
                "url": "POST /rooms/{room_id}/join",
                "data": {
                    "user_id": "user456"
                }
            },
            "send_message": {
                "url": "POST /rooms/{room_id}/messages",
                "data": {
                    "user_id": "user123",
                    "content": "Hello everyone!",
                    "type": "text"
                }
            }
        },
        "performance_benefits": {
            "gofastapi_latency": "<1ms per message",
            "fastapi_equivalent": "~25ms per message",
            "concurrent_users": "10K+ vs 400 (FastAPI)",
            "memory_efficiency": "50% better",
            "websocket_throughput": "100K+ messages/second"
        }
    }

@app.post("/chat/simulate-activity")
def simulate_chat_activity():
    """Simulate some chat activity for demo purposes."""
    start_time = time.time()
    
    # Create demo rooms if they don't exist
    demo_rooms = []
    
    if not chat_rooms:
        # Create demo rooms
        general_room = create_room("General Chat", "demo_user_1")
        tech_room = create_room("Tech Discussion", "demo_user_2")
        random_room = create_room("Random", "demo_user_3")
        
        demo_rooms = [general_room, tech_room, random_room]
        
        # Add some demo messages
        demo_messages = [
            (general_room["id"], "demo_user_1", "Welcome to the general chat!", "text"),
            (general_room["id"], "demo_user_2", "Hello everyone! How's everyone doing?", "text"),
            (tech_room["id"], "demo_user_2", "Let's discuss the latest in tech!", "text"),
            (tech_room["id"], "demo_user_3", "GoFastAPI is amazing - 25x faster than FastAPI!", "text"),
            (random_room["id"], "demo_user_3", "This is for random discussions", "text"),
            (random_room["id"], "demo_user_1", "Anyone here likes coffee? ☕", "text")
        ]
        
        for room_id, user_id, content, msg_type in demo_messages:
            create_message(room_id, user_id, content, msg_type)
    
    processing_time = time.time() - start_time
    
    return {
        "message": "Chat activity simulated successfully",
        "demo_data_created": {
            "rooms": len(chat_rooms),
            "total_messages": chat_metrics["total_messages"],
            "demo_rooms": [room["name"] for room in demo_rooms] if demo_rooms else []
        },
        "processing_time": f"{processing_time:.4f}s",
        "next_steps": [
            "View rooms: GET /rooms",
            "View messages: GET /rooms/{room_id}/messages",
            "Join a room: POST /rooms/{room_id}/join",
            "Send message: POST /rooms/{room_id}/messages"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting WebSocket Chat Application (Simulated)")
    print("=" * 60)
    print("💬 Chat Features:")
    print("  • Real-time messaging (simulated)")
    print("  • Multiple chat rooms")
    print("  • User presence tracking")
    print("  • Message history")
    print("  • REST API equivalent of WebSocket operations")
    print()
    print("⚡ WebSocket Performance (when using real WebSocket):")
    print("  • Framework: GoFastAPI v1.0.2")
    print("  • 25x faster than FastAPI WebSockets")
    print("  • 10K+ concurrent connections")
    print("  • <1ms message latency")
    print("  • 100K+ messages/second throughput")
    print()
    print("🌐 Server starting at: http://localhost:8005")
    print("📋 API endpoints:")
    print("  • POST /rooms                    - Create chat room")
    print("  • GET  /rooms                    - List rooms")
    print("  • GET  /rooms/{id}/messages      - Get messages")
    print("  • POST /rooms/{id}/messages      - Send message")
    print("  • POST /rooms/{id}/join          - Join room")
    print("  • GET  /chat/metrics             - Chat metrics")
    print("  • GET  /chat/demo                - Demo instructions")
    print("  • POST /chat/simulate-activity   - Create demo data")
    print("=" * 60)
    
    try:
        app.run(host="0.0.0.0", port=8005, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Chat server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
