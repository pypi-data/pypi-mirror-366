#!/usr/bin/env python3
"""
Comprehensive demo of Docker plugin approaches for yaapp.
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

def demo_class_based_plugin():
    """Demo the class-based Docker plugin (recommended)."""
    print("🐳 Demo: Class-Based Docker Plugin (Recommended)")
    print("=" * 60)
    
    try:
        from yaapp.plugins.docker.plugin import Docker
        
        # Create plugin instance
        docker_plugin = Docker()
        
        if not docker_plugin.client:
            print("❌ Docker daemon not available")
            return False
        
        print("✅ Docker plugin initialized")
        
        # Test basic connectivity
        ping_result = docker_plugin.ping()
        if ping_result.is_ok():
            print("✅ Docker daemon responding")
        else:
            print(f"❌ Docker ping failed: {ping_result.as_error}")
            return False
        
        # Get system info
        info_result = docker_plugin.get_system_info()
        if info_result.is_ok():
            info = info_result.unwrap()
            print(f"📊 System Info:")
            print(f"   Containers: {info.get('containers', 0)}")
            print(f"   Images: {info.get('images', 0)}")
            print(f"   Server Version: {info.get('server_version', 'Unknown')}")
        
        # List containers
        containers_result = docker_plugin.list_containers(all=True)
        if containers_result.is_ok():
            containers = containers_result.unwrap()
            print(f"📦 Containers: {len(containers)} found")
            for container in containers[:3]:
                print(f"   - {container['name']} ({container['status']})")
        
        # List images
        images_result = docker_plugin.list_images()
        if images_result.is_ok():
            images = images_result.unwrap()
            print(f"🖼️  Images: {len(images)} found")
            for image in images[:3]:
                tags = image['tags'][0] if image['tags'] else image['id'][:12]
                print(f"   - {tags}")
        
        print("✅ Class-based plugin demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Class-based plugin demo failed: {e}")
        return False

def demo_direct_client_exposure():
    """Demo direct Docker client exposure."""
    print("\n🐳 Demo: Direct Docker Client Exposure")
    print("=" * 60)
    
    try:
        import docker
        from yaapp import yaapp
        
        # Create Docker client
        client = docker.from_env()
        client.ping()  # Test connection
        print("✅ Docker client connected")
        
        # Expose client directly
        yaapp.expose(client, name="docker_direct")
        print("✅ Docker client exposed directly")
        
        # Get the exposed object
        registry = yaapp.get_registry_items()
        if 'docker_direct' in registry:
            docker_obj = registry['docker_direct']
            
            # Test direct method calls
            ping_result = docker_obj.ping()
            print(f"✅ Direct ping: {ping_result}")
            
            version_info = docker_obj.version()
            print(f"✅ Direct version: {version_info.get('Version', 'Unknown')}")
            
            containers = docker_obj.containers.list()
            print(f"✅ Direct containers list: {len(containers)} containers")
            
            images = docker_obj.images.list()
            print(f"✅ Direct images list: {len(images)} images")
        
        print("✅ Direct client exposure demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Direct client exposure demo failed: {e}")
        return False

def demo_simple_wrapper():
    """Demo the simple Docker wrapper."""
    print("\n🐳 Demo: Simple Docker Wrapper")
    print("=" * 60)
    
    try:
        from yaapp.plugins.docker.simple_exposure import SimpleDockerWrapper
        from yaapp import yaapp
        
        # Create wrapper
        wrapper = SimpleDockerWrapper()
        print("✅ Simple wrapper created")
        
        # Test methods
        ping_result = wrapper.ping()
        print(f"✅ Wrapper ping: {ping_result}")
        
        containers = wrapper.list_containers()
        print(f"✅ Wrapper containers: {len(containers)} found")
        
        images = wrapper.list_images()
        print(f"✅ Wrapper images: {len(images)} found")
        
        version = wrapper.version()
        print(f"✅ Wrapper version: {version.get('Version', 'Unknown')}")
        
        # Expose wrapper
        yaapp.expose(wrapper, name="docker_simple")
        print("✅ Simple wrapper exposed")
        
        print("✅ Simple wrapper demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Simple wrapper demo failed: {e}")
        return False

def demo_individual_methods():
    """Demo individual method exposure."""
    print("\n🐳 Demo: Individual Method Exposure")
    print("=" * 60)
    
    try:
        import docker
        from yaapp import yaapp
        
        # Create Docker client
        client = docker.from_env()
        
        # Expose individual methods
        yaapp.expose(client.ping, name="docker_ping")
        yaapp.expose(client.version, name="docker_version")
        yaapp.expose(client.containers.list, name="docker_list_containers")
        yaapp.expose(client.images.list, name="docker_list_images")
        
        print("✅ Individual methods exposed")
        
        # Test individual methods
        registry = yaapp.get_registry_items()
        
        if 'docker_ping' in registry:
            ping_func = registry['docker_ping']
            result = ping_func()
            print(f"✅ Individual ping: {result}")
        
        if 'docker_version' in registry:
            version_func = registry['docker_version']
            result = version_func()
            print(f"✅ Individual version: {result.get('Version', 'Unknown')}")
        
        if 'docker_list_containers' in registry:
            list_func = registry['docker_list_containers']
            result = list_func()
            print(f"✅ Individual list containers: {len(result)} containers")
        
        print("✅ Individual methods demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Individual methods demo failed: {e}")
        return False

def main():
    """Run all demos."""
    print("🐳 Docker Plugin Comprehensive Demo")
    print("=" * 80)
    
    results = {}
    
    # Run all demos
    results['class_based'] = demo_class_based_plugin()
    results['direct_client'] = demo_direct_client_exposure()
    results['simple_wrapper'] = demo_simple_wrapper()
    results['individual_methods'] = demo_individual_methods()
    
    # Summary
    print("\n📊 Demo Results Summary")
    print("=" * 40)
    for approach, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {approach.replace('_', ' ').title()}: {status}")
    
    # Recommendations
    print("\n💡 Recommendations")
    print("=" * 40)
    print("   🏆 Production: Use class-based plugin (@yaapp.expose('docker'))")
    print("   🚀 Prototyping: Use direct client (yaapp.expose(docker.from_env()))")
    print("   🔧 Custom: Create wrapper or expose specific methods")
    print("   📚 Documentation: See README.md for detailed usage")
    
    # Show available approaches
    print("\n🛠️  Available Approaches")
    print("=" * 40)
    print("   1. @yaapp.expose('docker') class Docker: ... (RECOMMENDED)")
    print("   2. yaapp.expose(docker.from_env(), name='docker')")
    print("   3. yaapp.expose(SimpleDockerWrapper(), name='docker')")
    print("   4. yaapp.expose(client.ping, name='docker_ping')")

if __name__ == "__main__":
    main()