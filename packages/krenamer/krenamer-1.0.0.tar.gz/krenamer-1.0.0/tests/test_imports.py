#!/usr/bin/env python3
"""
Pytest-based import and installation tests for KRenamer
"""

import sys
import pytest
from pathlib import Path

# Add src to path for testing
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


class TestImports:
    """Test KRenamer module imports"""
    
    def test_core_import(self):
        """Test KRenamer core module import"""
        from krenamer.core import RenameEngine
        assert RenameEngine
        
        # Test basic instantiation
        engine = RenameEngine()
        assert hasattr(engine, 'files')
        assert hasattr(engine, 'method')
    
    def test_gui_import(self):
        """Test KRenamer GUI module import"""
        from krenamer.gui import RenamerGUI
        assert RenamerGUI
        
        # Test that it has expected methods
        expected_methods = ['setup_window', 'setup_widgets', 'run']
        gui_methods = [method for method in dir(RenamerGUI) if not method.startswith('_')]
        
        for method in expected_methods:
            assert method in gui_methods, f"Method {method} should exist in RenameGUI"
    
    def test_main_import(self):
        """Test KRenamer main module import"""
        from krenamer.main import main
        assert callable(main)
    
    def test_package_structure(self):
        """Test package structure and __init__"""
        import krenamer
        assert hasattr(krenamer, '__version__')


class TestBasicFunctionality:
    """Test basic KRenamer functionality"""
    
    def test_engine_basic_operations(self):
        """Test basic engine operations"""
        from krenamer.core import RenameEngine
        
        engine = RenameEngine()
        
        # Test setting properties
        engine.method = "prefix"
        engine.prefix_text = "test_"
        assert engine.method == "prefix"
        assert engine.prefix_text == "test_"
        
        # Test file operations (with non-existent files)
        test_files = ["nonexistent1.txt", "nonexistent2.txt"]
        added = engine.add_files(test_files)
        assert added == 0  # Non-existent files should not be added
        assert len(engine.files) == 0
    
    def test_rename_plan_generation(self):
        """Test rename plan generation"""
        from krenamer.core import RenameEngine
        
        engine = RenameEngine()
        engine.method = "prefix"
        engine.prefix_text = "test_"
        
        # Should not crash even with no files
        plan = engine.generate_rename_plan()
        assert isinstance(plan, list)
    
    def test_condition_settings(self):
        """Test condition settings don't crash"""
        from krenamer.core import RenameEngine
        
        engine = RenameEngine()
        
        # These should not crash even with no files
        engine.use_size_condition = True
        engine.size_value = 1.0
        engine.size_operator = ">"
        engine.size_unit = "MB"
        
        engine.use_date_condition = True
        engine.date_operator = "after"
        
        engine.use_ext_condition = True
        engine.allowed_extensions = ".txt,.pdf"
        
        # Should generate empty plan without crashing
        plan = engine.generate_rename_plan()
        assert isinstance(plan, list)


class TestDependencies:
    """Test required and optional dependencies"""
    
    def test_tkinter_available(self):
        """Test that tkinter is available"""
        import tkinter as tk
        
        # Try to create a root window (without displaying it)
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.destroy()
        except tk.TclError:
            pytest.skip("No display available (normal in CI/server environments)")
    
    def test_tkinterdnd2_optional(self):
        """Test tkinterdnd2 availability (optional dependency)"""
        try:
            import tkinterdnd2
            assert tkinterdnd2  # Available - drag & drop will work
        except ImportError:
            # Not available - this is okay, drag & drop just won't work
            pass


class TestChapterExamples:
    """Test chapter examples availability"""
    
    def test_chapter_examples_exist(self):
        """Test that chapter examples exist"""
        chapters = []
        for i in range(1, 5):
            chapter_path = project_root / "src" / f"renamer-ch{i}" / "main.py"
            if chapter_path.exists():
                chapters.append(f"Chapter {i}")
        
        # It's okay if no chapters exist, but if they do, record them
        print(f"Found chapters: {chapters}" if chapters else "No chapter examples found")


class TestFileOperations:
    """Test file operation capabilities with real files"""
    
    def test_with_real_files(self, temp_files):
        """Test engine with real temporary files"""
        test_files, temp_dir = temp_files
        
        from krenamer.core import RenameEngine
        engine = RenameEngine()
        
        # Add real files
        added = engine.add_files(test_files)
        assert added == len(test_files)
        assert len(engine.files) == len(test_files)
        
        # Test rename plan with real files
        engine.method = "prefix"
        engine.prefix_text = "renamed_"
        
        plan = engine.generate_rename_plan()
        assert len(plan) == len(test_files)
        
        # All files should match (no conditions set)
        matching = [matches for _, _, matches in plan]
        assert all(matching)
        
        # Check that new names have prefix
        for _, new_name, matches in plan:
            if matches:
                assert new_name.startswith("renamed_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])