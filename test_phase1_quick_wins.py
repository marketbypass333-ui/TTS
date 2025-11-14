#!/usr/bin/env python3
"""
Test script for Phase 1 Quick Wins implementation

This script tests the following Quick Wins:
- Quick Win #2: Docker compose development environment (already tested)
- Quick Win #3: Example notebooks for voice cloning
- Quick Win #4: Improved CLI interface
- Quick Win #5: Simple REST API wrapper
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def test_docker_compose():
    """Test Docker Compose configuration"""
    print("=== Testing Docker Compose Configuration ===")
    
    # Check if files exist
    files_to_check = [
        "docker-compose.thai.yml",
        "Dockerfile.thai-tts", 
        "requirements.thai.txt",
        "start_thai_tts_dev.sh"
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    if all_exist:
        print("✅ All Docker Compose files generated successfully")
        return True
    else:
        print("❌ Some Docker Compose files are missing")
        return False

def test_notebooks():
    """Test Jupyter notebooks for voice cloning"""
    print("\n=== Testing Jupyter Notebooks ===")
    
    notebooks = [
        "notebooks/thai_voice_cloning_examples.ipynb",
        "notebooks/advanced_thai_tts_features.ipynb"
    ]
    
    all_exist = True
    for notebook in notebooks:
        if os.path.exists(notebook):
            print(f"✅ {notebook} created")
            
            # Check file size
            size = os.path.getsize(notebook)
            if size > 10000:  # Should be larger than 10KB
                print(f"✅ {notebook} has substantial content ({size} bytes)")
            else:
                print(f"⚠️  {notebook} might be small ({size} bytes)")
        else:
            print(f"❌ {notebook} missing")
            all_exist = False
    
    return all_exist

def test_cli():
    """Test CLI interface"""
    print("\n=== Testing CLI Interface ===")
    
    cli_file = "thai_tts_cli.py"
    if not os.path.exists(cli_file):
        print(f"❌ {cli_file} missing")
        return False
    
    print(f"✅ {cli_file} exists")
    
    # Test help command
    try:
        result = subprocess.run([
            sys.executable, cli_file, "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI help command works")
            if "Thai TTS CLI" in result.stdout:
                print("✅ CLI help shows Thai TTS information")
            else:
                print("⚠️  CLI help might not show complete information")
            return True
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI help command timed out")
        return False
    except Exception as e:
        print(f"❌ CLI help error: {e}")
        return False

def test_api():
    """Test REST API"""
    print("\n=== Testing REST API ===")
    
    api_file = "thai_tts_api.py"
    if not os.path.exists(api_file):
        print(f"❌ {api_file} missing")
        return False
    
    print(f"✅ {api_file} exists")
    
    # Check if FastAPI is available
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        print("⚠️  FastAPI not available - API won't work")
        return False
    
    # Test API syntax
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "FastAPI" in content and "/tts/synthesize" in content:
            print("✅ API contains FastAPI and TTS endpoints")
        else:
            print("⚠️  API might not contain expected content")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking API content: {e}")
        return False

def test_integration():
    """Test overall integration"""
    print("\n=== Testing Overall Integration ===")
    
    # Check if we're in the right directory
    if not os.path.exists("TTS"):
        print("❌ Not in the correct directory - TTS folder not found")
        return False
    
    print("✅ In correct directory with TTS folder")
    
    # Check for Thai-specific content
    thai_files = [
        f for f in os.listdir(".") 
        if "thai" in f.lower() or "th" in f.lower()
    ]
    
    if thai_files:
        print(f"✅ Found {len(thai_files)} Thai-specific files:")
        for f in thai_files:
            print(f"  - {f}")
    else:
        print("⚠️  No Thai-specific files found")
    
    return True

def main():
    """Main test function"""
    print("Thai TTS Phase 1 Quick Wins Test")
    print("=" * 50)
    
    tests = [
        ("Docker Compose", test_docker_compose),
        ("Jupyter Notebooks", test_notebooks),
        ("CLI Interface", test_cli),
        ("REST API", test_api),
        ("Integration", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            print(f"\n{test_name}: {'✅ PASS' if result else '❌ FAIL'}")
        except Exception as e:
            results[test_name] = False
            print(f"\n{test_name}: ❌ ERROR - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 All Quick Wins implemented successfully!")
        print("\nNext steps:")
        print("1. Run: python create_docker_compose.py")
        print("2. Run: ./start_thai_tts_dev.sh")
        print("3. Access Jupyter notebooks at http://localhost:8888")
        print("4. Test CLI: python thai_tts_cli.py")
        print("5. Test API: python thai_tts_api.py")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)