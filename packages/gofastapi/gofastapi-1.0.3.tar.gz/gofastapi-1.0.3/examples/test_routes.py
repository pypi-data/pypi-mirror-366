#!/usr/bin/env python3
"""
Test script để kiểm tra phản hồi của các routes trong basic_api.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_route_responses():
    print("🔍 KIỂM TRA PHẢN HỒI CỦA CÁC ROUTES")
    print("=" * 50)
    
    try:
        # Import module
        import basic_api
        print("✅ Module imported successfully")
        
        # Test từng route một cách chi tiết
        print("\n📋 TESTING INDIVIDUAL ROUTES:")
        
        # 1. Test root route
        print("\n1. Testing ROOT route (/)...")
        try:
            response = basic_api.root()
            print(f"✅ Root route response type: {type(response)}")
            print(f"✅ Root route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   Framework: {response.get('framework', 'Missing')}")
                print(f"   Version: {response.get('version', 'Missing')}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ Root route error: {e}")
            import traceback
            traceback.print_exc()
        
        # 2. Test health route
        print("\n2. Testing HEALTH route (/health)...")
        try:
            response = basic_api.health_check()
            print(f"✅ Health route response type: {type(response)}")
            print(f"✅ Health route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   Status: {response.get('status', 'Missing')}")
                print(f"   Version: {response.get('version', 'Missing')}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ Health route error: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Test user registration
        print("\n3. Testing USER REGISTRATION route (/auth/register)...")
        try:
            test_user = {
                "username": "test_route_user",
                "email": "test@route.com",
                "password": "test123",
                "full_name": "Test Route User"
            }
            response = basic_api.register_user(test_user)
            print(f"✅ Register route response type: {type(response)}")
            print(f"✅ Register route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   Message: {response.get('message', 'Missing')}")
                print(f"   User created: {response.get('user', {}).get('username', 'Missing')}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ Register route error: {e}")
        
        # 4. Test login
        print("\n4. Testing USER LOGIN route (/auth/login)...")
        try:
            # First create admin user
            admin_user = {
                "username": "admin_test",
                "email": "admin@test.com",
                "password": "admin123",
                "full_name": "Admin Test",
                "role": "admin"
            }
            basic_api.register_user(admin_user)
            
            credentials = {
                "username": "admin_test",
                "password": "admin123"
            }
            response = basic_api.login_user(credentials)
            print(f"✅ Login route response type: {type(response)}")
            print(f"✅ Login route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   Message: {response.get('message', 'Missing')}")
                print(f"   Token: {response.get('token', 'Missing')[:10]}...")
                print(f"   User: {response.get('user', {}).get('username', 'Missing')}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ Login route error: {e}")
        
        # 5. Test list users
        print("\n5. Testing LIST USERS route (/users)...")
        try:
            response = basic_api.list_users()
            print(f"✅ List users route response type: {type(response)}")
            print(f"✅ List users route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   Total users: {response.get('total', 'Missing')}")
                print(f"   Users array length: {len(response.get('users', []))}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ List users route error: {e}")
        
        # 6. Test list posts
        print("\n6. Testing LIST POSTS route (/posts)...")
        try:
            response = basic_api.list_posts()
            print(f"✅ List posts route response type: {type(response)}")
            print(f"✅ List posts route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   Total posts: {response.get('total', 'Missing')}")
                print(f"   Posts array length: {len(response.get('posts', []))}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ List posts route error: {e}")
        
        # 7. Test metrics
        print("\n7. Testing METRICS route (/metrics)...")
        try:
            response = basic_api.get_metrics()
            print(f"✅ Metrics route response type: {type(response)}")
            print(f"✅ Metrics route response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"   System info: {response.get('system', {}).get('framework', 'Missing')}")
                print(f"   Database info: {response.get('database', {})}")
            else:
                print(f"❌ Response is not a dictionary: {response}")
        except Exception as e:
            print(f"❌ Metrics route error: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 ROUTE RESPONSE ANALYSIS COMPLETE")
        print("=" * 50)
        
        # Kiểm tra app object
        print(f"\n🔧 APP OBJECT ANALYSIS:")
        print(f"   App type: {type(basic_api.app)}")
        print(f"   App title: {getattr(basic_api.app, 'title', 'Missing')}")
        print(f"   App version: {getattr(basic_api.app, 'version', 'Missing')}")
        
        # Kiểm tra routes được đăng ký
        if hasattr(basic_api.app, 'routes') or hasattr(basic_api.app, '_routes'):
            routes = getattr(basic_api.app, 'routes', getattr(basic_api.app, '_routes', []))
            print(f"   Registered routes: {len(routes)}")
            for i, route in enumerate(routes[:5]):  # Show first 5 routes
                print(f"     Route {i+1}: {route}")
        else:
            print("   No routes attribute found")
            
        return True
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_route_responses()
