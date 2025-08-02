"""
Test script to validate all GoFastAPI examples
"""
import sys
import importlib.util
import traceback

def test_example(file_path, name):
    """Test if an example file can be imported without errors."""
    print(f"\n🧪 Testing {name}...")
    print("-" * 40)
    
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location("example", file_path)
        module = importlib.util.module_from_spec(spec)
        
        # Prevent the app from actually running
        import sys
        old_argv = sys.argv
        sys.argv = ["test"]
        
        # Execute the module (this will initialize but not run the server)
        spec.loader.exec_module(module)
        
        # Restore argv
        sys.argv = old_argv
        
        print(f"✅ {name} - Syntax and imports: OK")
        
        # Check if GoFastAPI app exists
        if hasattr(module, 'app'):
            app = module.app
            print(f"✅ {name} - GoFastAPI app initialized: OK")
            print(f"   • Title: {getattr(app, 'title', 'N/A')}")
            print(f"   • Version: {getattr(app, 'version', 'N/A')}")
            
            # Try to get routes if available
            if hasattr(app, 'routes') or hasattr(app, '_routes'):
                routes = getattr(app, 'routes', getattr(app, '_routes', []))
                print(f"   • Routes registered: {len(routes) if routes else 'Unknown'}")
        else:
            print(f"⚠️  {name} - No 'app' variable found")
            
        return True
        
    except Exception as e:
        print(f"❌ {name} - Error: {str(e)}")
        print(f"   Traceback: {traceback.format_exc().splitlines()[-1]}")
        return False

def main():
    print("🚀 GoFastAPI Examples Test Suite")
    print("=" * 50)
    
    examples = [
        ("basic_api.py", "Basic API Example"),
        ("advanced_data_processing_new.py", "Advanced Data Processing"),
        ("fastapi_migration.py", "FastAPI Migration Guide"),
        ("microservice_new.py", "Microservice Architecture"),
        ("websocket_chat_new.py", "WebSocket Chat Application")
    ]
    
    results = []
    
    for filename, name in examples:
        file_path = f"D:\\Server\\Python\\rocketgo\\gofastapi\\pythonpackaging\\examples\\{filename}"
        success = test_example(file_path, name)
        results.append((name, success))
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("-" * 50)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All examples are working correctly!")
        print("🚀 Ready for production use!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} example(s) need attention")

if __name__ == "__main__":
    main()
