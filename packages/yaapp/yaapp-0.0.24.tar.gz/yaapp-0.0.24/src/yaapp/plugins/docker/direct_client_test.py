"""
Test script to explore direct Docker client exposure.
This tests if yaapp.expose(client) works directly with the Docker client.
"""

import docker
from yaapp import yaapp

def test_direct_client_exposure():
    """Test if we can directly expose the Docker client."""
    
    print("🧪 Testing direct Docker client exposure...")
    
    try:
        # Create Docker client
        client = docker.from_env()
        client.ping()  # Test connection
        print("✅ Docker client connected successfully")
        
        # Try to expose the client directly
        print("📡 Attempting to expose Docker client directly...")
        yaapp.expose(client, name="docker_direct")
        print("✅ Direct client exposure successful!")
        
        # Check what methods are available
        registry_items = yaapp.get_registry_items()
        docker_items = {k: v for k, v in registry_items.items() if k.startswith("docker_direct")}
        
        print(f"📋 Exposed Docker client methods ({len(docker_items)}):")
        for name, obj in docker_items.items():
            print(f"   - {name}: {type(obj)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Direct client exposure failed: {e}")
        return False

def test_class_based_exposure():
    """Test the class-based approach for comparison."""
    
    print("\n🧪 Testing class-based Docker plugin exposure...")
    
    try:
        # Import our Docker plugin
        from .plugin import Docker
        
        # Create and expose the plugin
        docker_plugin = Docker()
        yaapp.expose(docker_plugin, name="docker_class")
        print("✅ Class-based exposure successful!")
        
        # Check what methods are available
        registry_items = yaapp.get_registry_items()
        docker_items = {k: v for k, v in registry_items.items() if k.startswith("docker_class")}
        
        print(f"📋 Exposed Docker plugin methods ({len(docker_items)}):")
        for name, obj in docker_items.items():
            print(f"   - {name}: {type(obj)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Class-based exposure failed: {e}")
        return False

if __name__ == "__main__":
    print("🐳 Docker Plugin Exposure Test")
    print("=" * 50)
    
    # Test both approaches
    direct_success = test_direct_client_exposure()
    class_success = test_class_based_exposure()
    
    print("\n📊 Results Summary:")
    print(f"   Direct client exposure: {'✅ Success' if direct_success else '❌ Failed'}")
    print(f"   Class-based exposure:   {'✅ Success' if class_success else '❌ Failed'}")
    
    if direct_success:
        print("\n💡 Direct client exposure works! You can use:")
        print("   client = docker.from_env()")
        print("   yaapp.expose(client, name='docker')")
    
    if class_success:
        print("\n💡 Class-based exposure works! You can use:")
        print("   @yaapp.expose('docker')")
        print("   class Docker: ...")