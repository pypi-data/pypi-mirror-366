"""
FastAPI Migration Guide - Drop-in replacement example

This file demonstrates how to migrate from FastAPI to GoFastAPI
with zero code changes required!
"""

# Traditional FastAPI import
# from fastapi import FastAPI

# GoFastAPI drop-in replacement - just change the import!
from gofastapi import FastAPI

# Your existing FastAPI code works unchanged!
app = FastAPI(
    title="My Migrated API",
    description="Migrated from FastAPI to GoFastAPI - 25x faster!",
    version="2.0.0"
)

@app.get("/")
def read_root():
    """Root endpoint - same code, 25x faster performance!"""
    return {"Hello": "World", "Framework": "GoFastAPI", "Performance": "25x faster"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """Item endpoint with path and query parameters."""
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def create_item(item: dict):
    """Create item endpoint."""
    return {"created": item, "performance": "Ultra-fast processing"}

if __name__ == "__main__":
    print("🚀 FastAPI to GoFastAPI Migration Example")
    print("💡 Same code, 25x better performance!")
    app.run(host="0.0.0.0", port=8000, reload=True)
