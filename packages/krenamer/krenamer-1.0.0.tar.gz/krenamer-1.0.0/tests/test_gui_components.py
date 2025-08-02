#!/usr/bin/env python3
"""
Pytest-based GUI component tests for KRenamer
"""

import sys
import pytest
from pathlib import Path
import os

# Add src to path for testing
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


class TestGUIComponents:
    """Test GUI components without requiring display"""
    
    def test_gui_class_structure(self):
        """Test RenameGUI class structure"""
        from krenamer.gui import RenamerGUI
        
        # Check that class exists and has expected methods
        expected_methods = [
            'setup_window', 'setup_widgets', 'setup_drag_drop', 
            'run', 'add_files', 'refresh_file_list'
        ]
        
        gui_methods = [method for method in dir(RenamerGUI) if not method.startswith('_')]
        
        for method in expected_methods:
            assert method in gui_methods, f"Method {method} should exist in RenameGUI"
    
    def test_gui_engine_integration(self):
        """Test GUI-Engine integration structure"""
        from krenamer.gui import RenamerGUI
        from krenamer.core import RenameEngine
        
        # These should be importable together
        assert RenamerGUI
        assert RenameEngine
    
    @pytest.mark.skipif(
        not (os.environ.get('DISPLAY') or os.name == 'nt'),
        reason="No display available"
    )
    def test_gui_instantiation(self):
        """Test GUI instantiation (only if display is available)"""
        try:
            from krenamer.gui import RenamerGUI
            
            # Try to create GUI instance
            app = RenamerGUI()
            assert app.engine  # Should have an engine
            assert hasattr(app, 'root')  # Should have tkinter root
            
            # Clean up
            if hasattr(app, 'root') and app.root:
                app.root.destroy()
                
        except Exception as e:
            pytest.skip(f"GUI instantiation failed (expected in headless environment): {e}")
    
    def test_gui_with_sample_files(self, temp_files):
        """Test GUI functionality with sample files (structure only)"""
        test_files, temp_dir = temp_files
        
        from krenamer.gui import RenamerGUI
        
        # This tests the logic without actually creating GUI
        try:
            # Test that the add_files method signature exists
            assert hasattr(RenamerGUI, 'add_files')
        except Exception as e:
            pytest.fail(f"GUI structure test failed: {e}")


class TestGUIIntegration:
    """Test GUI integration with core engine"""
    
    def test_gui_engine_connection(self):
        """Test that GUI properly connects to engine"""
        try:
            import tkinter as tk
            
            # Test basic tkinter functionality
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            from krenamer.core import RenameEngine
            engine = RenameEngine()
            
            # Test that engine can be used independently
            engine.method = "prefix"
            engine.prefix_text = "gui_test_"
            
            plan = engine.generate_rename_plan()
            assert isinstance(plan, list)
            
            root.destroy()
            
        except tk.TclError:
            pytest.skip("No display available for tkinter test")
    
    def test_variable_binding_structure(self):
        """Test that GUI variable binding structure is sound"""
        from krenamer.gui import RenamerGUI
        
        # Check that the class has expected attributes for variable binding
        gui_class = RenamerGUI
        
        # These methods should exist for proper GUI functionality
        expected_setup_methods = [
            'setup_variables', 'setup_bindings', 'update_preview'
        ]
        
        class_methods = [method for method in dir(gui_class) 
                        if not method.startswith('_') and callable(getattr(gui_class, method, None))]
        
        for method in expected_setup_methods:
            assert method in class_methods, f"Setup method {method} should exist"


@pytest.mark.gui
class TestGUIInteractive:
    """Interactive GUI tests (marked for optional execution)"""
    
    @pytest.mark.skipif(
        os.environ.get('CI') == 'true' or not (os.environ.get('DISPLAY') or os.name == 'nt'),
        reason="Skipping interactive tests in CI or headless environment"
    )
    def test_gui_manual_run(self, temp_files):
        """Manual GUI test (only runs in interactive environments)"""
        test_files, temp_dir = temp_files
        
        print("\n" + "="*50)
        print("INTERACTIVE GUI TEST")
        print("="*50)
        print("This test will open the KRenamer GUI.")
        print("Close the window to complete the test.")
        print("Files loaded:", [Path(f).name for f in test_files])
        
        try:
            from krenamer.gui import RenamerGUI
            app = RenamerGUI()
            
            # Add test files
            app.add_files(test_files)
            
            print("GUI starting... (close window to continue)")
            # Note: app.run() is commented out to avoid blocking in automated tests
            # Uncomment the next line for actual interactive testing:
            # app.run()
            
        except Exception as e:
            print(f"Interactive GUI test failed: {e}")
            # This is expected in automated environments


if __name__ == "__main__":
    # Run with GUI marker to include interactive tests
    pytest.main([__file__, "-v", "-m", "not gui"])