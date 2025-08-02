#!/usr/bin/env python3
"""
HTTP Server wrapper cho GoFastAPI để các routes có thể phản hồi requests
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import basic_api module
import basic_api

class GoFastAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler cho GoFastAPI routes"""
    
    def _set_response(self, status_code=200, content_type="application/json"):
        """Set HTTP response headers"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _get_request_data(self):
        """Get request body data"""
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except:
                return {}
        return {}
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self._set_response(status_code)
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def _handle_route(self, method, path):
        """Handle route based on method and path"""
        try:
            request_data = self._get_request_data() if method in ['POST', 'PUT'] else {}
            
            # Route mapping
            if method == 'GET' and path == '/':
                result = basic_api.root()
                self._send_json_response(result)
                
            elif method == 'GET' and path == '/health':
                result = basic_api.health_check()
                self._send_json_response(result)
                
            elif method == 'POST' and path == '/auth/register':
                result = basic_api.register_user(request_data)
                self._send_json_response(result)
                
            elif method == 'POST' and path == '/auth/login':
                result = basic_api.login_user(request_data)
                self._send_json_response(result)
                
            elif method == 'POST' and path == '/auth/logout':
                result = basic_api.logout_user(request_data)
                self._send_json_response(result)
                
            elif method == 'GET' and path == '/users':
                result = basic_api.list_users()
                self._send_json_response(result)
                
            elif method == 'GET' and path.startswith('/users/'):
                user_id = int(path.split('/')[-1])
                result = basic_api.get_user(user_id)
                self._send_json_response(result)
                
            elif method == 'PUT' and path.startswith('/users/'):
                user_id = int(path.split('/')[-1])
                token = request_data.get('token')
                result = basic_api.update_user(user_id, request_data, token)
                self._send_json_response(result)
                
            elif method == 'GET' and path == '/posts':
                result = basic_api.list_posts()
                self._send_json_response(result)
                
            elif method == 'POST' and path == '/posts':
                token = request_data.get('token')
                result = basic_api.create_post(request_data, token)
                self._send_json_response(result)
                
            elif method == 'GET' and path.startswith('/posts/'):
                post_id = int(path.split('/')[-1])
                result = basic_api.get_post(post_id)
                self._send_json_response(result)
                
            elif method == 'GET' and path == '/metrics':
                result = basic_api.get_metrics()
                self._send_json_response(result)
                
            else:
                # Route not found
                self._send_json_response({
                    "detail": f"Route {method} {path} not found",
                    "available_routes": [
                        "GET /",
                        "GET /health", 
                        "POST /auth/register",
                        "POST /auth/login",
                        "POST /auth/logout",
                        "GET /users",
                        "GET /users/{id}",
                        "PUT /users/{id}",
                        "GET /posts",
                        "POST /posts",
                        "GET /posts/{id}",
                        "GET /metrics"
                    ]
                }, 404)
                
        except basic_api.HTTPException as e:
            self._send_json_response({
                "error": e.detail,
                "status_code": e.status_code
            }, e.status_code)
            
        except Exception as e:
            self._send_json_response({
                "error": str(e),
                "type": type(e).__name__
            }, 500)
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        self._handle_route('GET', path)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        self._handle_route('POST', path)
    
    def do_PUT(self):
        """Handle PUT requests"""
        path = urlparse(self.path).path
        self._handle_route('PUT', path)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS)"""
        self._set_response(200)
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"🌐 {self.address_string()} - {format % args}")

def run_server(host='localhost', port=8000):
    """Run the HTTP server"""
    print("🚀 STARTING GOFASTAPI HTTP SERVER")
    print("=" * 50)
    
    # Initialize sample data
    print("📊 Initializing sample data...")
    sample_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Administrator",
            "role": "admin"
        },
        {
            "username": "john_doe",
            "email": "john@example.com", 
            "password": "password123",
            "full_name": "John Doe",
            "role": "user"
        }
    ]
    
    for user_data in sample_users:
        try:
            basic_api.register_user(user_data)
            print(f"✅ Created user: {user_data['username']}")
        except Exception as e:
            if "already exists" in str(e):
                print(f"ℹ️  User {user_data['username']} already exists")
    
    print(f"\n🌐 Server starting at: http://{host}:{port}")
    print(f"📊 Users loaded: {len(basic_api.users_db)}")
    print(f"📊 Routes available: 12")
    print("\n📋 Available endpoints:")
    endpoints = [
        "GET  / - API Information",
        "GET  /health - Health Check", 
        "POST /auth/register - User Registration",
        "POST /auth/login - User Login",
        "POST /auth/logout - User Logout",
        "GET  /users - List Users",
        "GET  /users/{id} - Get User",
        "PUT  /users/{id} - Update User",
        "GET  /posts - List Posts",
        "POST /posts - Create Post",
        "GET  /posts/{id} - Get Post",
        "GET  /metrics - System Metrics"
    ]
    
    for endpoint in endpoints:
        print(f"  • {endpoint}")
    
    print("=" * 50)
    
    # Start server
    server = HTTPServer((host, port), GoFastAPIHandler)
    try:
        print(f"✅ Server running! Open http://{host}:{port} in your browser")
        print("Press Ctrl+C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        server.shutdown()
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    run_server()
