#!/usr/bin/env python3
"""Test the enhanced process command directly."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test if we can import the enhanced modules."""
    print("\n=== Testing imports ===")
    
    try:
        from vector_db_query.cli.commands.process_enhanced import process_command, detect_format, show_supported_formats
        print("✓ Successfully imported process_enhanced module")
        
        from vector_db_query.document_processor.reader import ReaderFactory
        print("✓ Successfully imported ReaderFactory")
        
        from vector_db_query.document_processor.image_ocr_reader import check_ocr_available, get_available_languages
        print("✓ Successfully imported OCR functions")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_reader_factory():
    """Test ReaderFactory functionality."""
    print("\n=== Testing ReaderFactory ===")
    
    try:
        from vector_db_query.document_processor.reader import ReaderFactory
        factory = ReaderFactory()
        
        print(f"✓ ReaderFactory initialized")
        print(f"✓ Supporting {len(factory.supported_extensions)} file extensions")
        
        # Show some supported extensions
        print("\nSample supported extensions:")
        for ext in sorted(factory.supported_extensions)[:10]:
            print(f"  - {ext}")
        print(f"  ... and {len(factory.supported_extensions) - 10} more")
        
        return True
    except Exception as e:
        print(f"✗ ReaderFactory test failed: {e}")
        return False

def test_ocr_functions():
    """Test OCR-related functions."""
    print("\n=== Testing OCR functions ===")
    
    try:
        from vector_db_query.document_processor.image_ocr_reader import check_ocr_available, get_available_languages
        
        ocr_available = check_ocr_available()
        print(f"OCR available: {ocr_available}")
        
        if ocr_available:
            languages = get_available_languages()
            print(f"✓ Available OCR languages: {len(languages)}")
            if languages:
                print(f"  Sample languages: {', '.join(languages[:5])}")
        
        return True
    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        return False

def test_show_formats():
    """Test show_supported_formats function."""
    print("\n=== Testing show_supported_formats ===")
    
    try:
        from vector_db_query.cli.commands.process_enhanced import show_supported_formats
        from rich.console import Console
        
        # Create a console that captures output
        import io
        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True)
        
        # Monkey patch the console in the module
        import vector_db_query.cli.commands.process_enhanced as pe
        original_console = pe.console
        pe.console = console
        
        # Call the function
        show_supported_formats()
        
        # Restore original console
        pe.console = original_console
        
        # Check output
        output = string_io.getvalue()
        if "Supported File Formats" in output:
            print("✓ show_supported_formats executed successfully")
            print("\nFormat categories found:")
            if "Documents" in output:
                print("  ✓ Documents")
            if "Spreadsheets" in output:
                print("  ✓ Spreadsheets")
            if "Images (OCR)" in output:
                print("  ✓ Images with OCR")
            return True
        else:
            print("✗ show_supported_formats did not produce expected output")
            return False
            
    except Exception as e:
        print(f"✗ show_supported_formats test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Enhanced Process Command")
    print("="*50)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_reader_factory():
        all_passed = False
        
    if not test_ocr_functions():
        all_passed = False
        
    if not test_show_formats():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        
    sys.exit(0 if all_passed else 1)