"""
Example: Basic GoFastAPI Application
Simple API server with CRUD operations
"""

from gofastapi import GoFastAPI

# Create application instance
app = GoFastAPI(
    title="Basic API Example",
    version="1.0.0",
    description="A simple API demonstrating basic GoFastAPI features"
)

# In-memory storage for demo
users_db = {}
next_id = 1


@app.get("/")
def root():
    """Root endpoint returning API information."""
    return {
        "name": "Basic GoFastAPI Example",
        "version": "1.0.0",
        "description": "Simple CRUD API with users",
        "endpoints": {
            "users": "/users",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "1.0.0"
    }


@app.get("/users")
def list_users():
    """Get all users."""
    return {
        "users": list(users_db.values()),
        "count": len(users_db)
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Get a specific user by ID."""
    if user_id not in users_db:
        return {"error": "User not found"}, 404
    
    return users_db[user_id]


@app.post("/users")
def create_user(user_data: dict):
    """Create a new user."""
    global next_id
    
    # Basic validation
    if not user_data.get("name") or not user_data.get("email"):
        return {"error": "Name and email are required"}, 400
    
    user = {
        "id": next_id,
        "name": user_data["name"],
        "email": user_data["email"],
        "active": user_data.get("active", True),
        "created_at": "2024-01-15T10:30:00Z"
    }
    
    users_db[next_id] = user
    next_id += 1
    
    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: dict):
    """Update an existing user."""
    if user_id not in users_db:
        return {"error": "User not found"}, 404
    
    user = users_db[user_id]
    
    # Update fields if provided
    if "name" in user_data:
        user["name"] = user_data["name"]
    if "email" in user_data:
        user["email"] = user_data["email"]
    if "active" in user_data:
        user["active"] = user_data["active"]
    
    user["updated_at"] = "2024-01-15T11:00:00Z"
    
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        return {"error": "User not found"}, 404
    
    deleted_user = users_db.pop(user_id)
    return {"message": "User deleted", "user": deleted_user}


@app.get("/metrics")
def get_metrics():
    """Get basic application metrics."""
    return {
        "total_users": len(users_db),
        "active_users": sum(1 for user in users_db.values() if user.get("active", True)),
        "memory_usage": "45MB",
        "uptime": "2h 30m"
    }


if __name__ == "__main__":
    # Add some sample data
    sample_users = [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"},
        {"name": "Bob Johnson", "email": "bob@example.com"}
    ]
    
    for user_data in sample_users:
        create_user(user_data)
    
    print("🚀 Starting Basic GoFastAPI Example")
    print("📋 Sample data loaded")
    print("🌐 Available at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    
    # Run the application
    app.run(host="0.0.0.0", port=8000, reload=True)
