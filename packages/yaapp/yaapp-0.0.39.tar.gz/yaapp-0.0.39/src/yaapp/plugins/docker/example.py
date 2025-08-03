"""
Example usage of the Docker plugin for yaapp.
Demonstrates both direct client exposure and class-based approach.
"""

import docker
from yaapp import Yaapp

def example_direct_client():
    """Example using direct Docker client exposure."""
    
    print("🐳 Example: Direct Docker Client Exposure")
    print("=" * 50)
    
    # Create yaapp instance
    app = Yaapp()
    
    try:
        # Create Docker client
        client = docker.from_env()
        
        # Expose the client directly
        app.expose(client, name="docker")
        
        print("✅ Docker client exposed directly!")
        print("Available methods:")
        
        # List some key methods that would be exposed
        registry_items = app.get_registry_items()
        docker_methods = [k for k in registry_items.keys() if k.startswith("docker")]
        
        for method in sorted(docker_methods)[:10]:  # Show first 10
            print(f"   - {method}")
        
        if len(docker_methods) > 10:
            print(f"   ... and {len(docker_methods) - 10} more methods")
            
        return app
        
    except Exception as e:
        print(f"❌ Failed to expose Docker client: {e}")
        return None

def example_class_based():
    """Example using class-based Docker plugin."""
    
    print("\n🐳 Example: Class-Based Docker Plugin")
    print("=" * 50)
    
    # Create yaapp instance
    app = Yaapp()
    
    try:
        # Import and create Docker plugin
        from .plugin import Docker
        
        docker_plugin = Docker()
        
        # The plugin is already exposed via @yaapp.expose("docker") decorator
        # But we can also expose it manually:
        # app.expose(docker_plugin, name="docker")
        
        print("✅ Docker plugin exposed via class!")
        print("Available methods:")
        
        # List the methods from our Docker class
        methods = [method for method in dir(docker_plugin) 
                  if not method.startswith('_') and callable(getattr(docker_plugin, method))]
        
        for method in sorted(methods):
            print(f"   - {method}")
            
        return app
        
    except Exception as e:
        print(f"❌ Failed to expose Docker plugin: {e}")
        return None

def demo_usage():
    """Demonstrate actual usage of Docker plugin methods."""
    
    print("\n🚀 Demo: Using Docker Plugin Methods")
    print("=" * 50)
    
    try:
        from .plugin import Docker
        
        docker_plugin = Docker()
        
        # Test basic connectivity
        print("🔍 Testing Docker connectivity...")
        ping_result = docker_plugin.ping()
        if ping_result.is_ok():
            print("✅ Docker daemon is responding")
        else:
            print(f"❌ Docker daemon not responding: {ping_result.as_error}")
            return
        
        # Get system info
        print("\n📊 Getting Docker system info...")
        info_result = docker_plugin.get_system_info()
        if info_result.is_ok():
            info = info_result.unwrap()
            print(f"   Containers: {info.get('containers', 0)}")
            print(f"   Images: {info.get('images', 0)}")
            print(f"   Server Version: {info.get('server_version', 'Unknown')}")
        
        # List containers
        print("\n📦 Listing containers...")
        containers_result = docker_plugin.list_containers(all=True)
        if containers_result.is_ok():
            containers = containers_result.unwrap()
            if containers:
                for container in containers[:3]:  # Show first 3
                    print(f"   - {container['name']} ({container['status']})")
                if len(containers) > 3:
                    print(f"   ... and {len(containers) - 3} more containers")
            else:
                print("   No containers found")
        
        # List images
        print("\n🖼️  Listing images...")
        images_result = docker_plugin.list_images()
        if images_result.is_ok():
            images = images_result.unwrap()
            if images:
                for image in images[:3]:  # Show first 3
                    tags = image['tags'][0] if image['tags'] else image['id'][:12]
                    print(f"   - {tags}")
                if len(images) > 3:
                    print(f"   ... and {len(images) - 3} more images")
            else:
                print("   No images found")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    print("🐳 Docker Plugin Examples for yaapp")
    print("=" * 60)
    
    # Try direct client exposure
    direct_app = example_direct_client()
    
    # Try class-based approach
    class_app = example_class_based()
    
    # Demo actual usage
    demo_usage()
    
    print("\n💡 Recommendations:")
    print("   - Use direct client exposure for quick prototyping")
    print("   - Use class-based approach for production (better error handling)")
    print("   - Class-based approach provides Result pattern for consistent error handling")
    print("   - Direct exposure gives you all Docker client methods automatically")