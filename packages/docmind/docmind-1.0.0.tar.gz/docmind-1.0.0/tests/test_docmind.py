#!/usr/bin/env python3
"""Simple test to verify DocMind package structure."""

def test_imports():
    """Test that all main components can be imported."""
    try:
        from docmind import DocMind, DocMindConfig
        from docmind.config import load_config, get_preset_config
        from docmind.exceptions import DocMindError
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_presets():
    """Test configuration presets."""
    try:
        from docmind.config import QUALITY_PRESETS, get_preset_config
        
        for preset_name in QUALITY_PRESETS:
            config = get_preset_config(preset_name)
            print(f"✅ Preset '{preset_name}' loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_basic_initialization():
    """Test basic DocMind initialization."""
    try:
        from docmind import DocMind
        from docmind.config import DocMindConfig
        
        # Test basic initialization
        converter = DocMind(output_dir="test_output")
        print("✅ Basic DocMind initialized")
        
        # Test with config
        config = DocMindConfig()
        converter_with_config = DocMind(config, "test_output")
        print("✅ DocMind with config initialized")
        
        return True
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing DocMind Package Structure")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Presets", test_config_presets), 
        ("Initialization", test_basic_initialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package structure is correct.")
    else:
        print("⚠️  Some tests failed. Check dependencies.")
        exit(1)