#!/usr/bin/env python3
"""
Comprehensive tests for KRenamer core functionality
"""

import sys
import pytest
from pathlib import Path
import tempfile
import os

# Add src to path for testing
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from krenamer.core import RenameEngine


class TestRenameEngine:
    """Test cases for RenameEngine class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.engine = RenameEngine()
        
        # Create temporary test files
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_files = []
        
        for i in range(3):
            test_file = self.temp_dir / f"test_file_{i}.txt"
            test_file.write_text(f"Test content {i}")
            self.test_files.append(str(test_file))
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Clean up temporary files
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.files == []
        assert self.engine.method == "prefix"
        assert hasattr(self.engine, 'prefix_text')
        assert hasattr(self.engine, 'suffix_text')
    
    def test_add_files(self):
        """Test adding files to engine"""
        # Test adding existing files
        added = self.engine.add_files(self.test_files)
        assert added == len(self.test_files)
        assert len(self.engine.files) == len(self.test_files)
        
        # Test adding non-existent files
        fake_files = ["nonexistent1.txt", "nonexistent2.txt"]
        added = self.engine.add_files(fake_files)
        assert added == 0
        assert len(self.engine.files) == len(self.test_files)  # Should not change
    
    def test_remove_files(self):
        """Test removing files from engine"""
        self.engine.add_files(self.test_files)
        
        # Remove by indices
        self.engine.remove_files_by_indices([0, 2])
        assert len(self.engine.files) == 1
        
        # Clear all files
        self.engine.clear_files()
        assert len(self.engine.files) == 0
    
    def test_basic_rename_methods(self):
        """Test basic rename methods"""
        self.engine.add_files(self.test_files)
        
        # Test prefix method
        self.engine.method = "prefix"
        self.engine.prefix_text = "new_"
        plan = self.engine.generate_rename_plan()
        
        for original_path, new_name, matches in plan:
            if matches:
                assert new_name.startswith("new_")
        
        # Test suffix method
        self.engine.method = "suffix"
        self.engine.suffix_text = "_new"
        plan = self.engine.generate_rename_plan()
        
        for original_path, new_name, matches in plan:
            if matches:
                assert "_new.txt" in new_name
    
    def test_numbering_method(self):
        """Test numbering rename method"""
        self.engine.add_files(self.test_files)
        
        self.engine.method = "number"
        self.engine.start_number = 10
        plan = self.engine.generate_rename_plan()
        
        expected_numbers = [10, 11, 12]
        actual_numbers = []
        
        for original_path, new_name, matches in plan:
            if matches:
                # Extract number from filename like "010_test_file_0.txt"
                parts = new_name.split("_")
                if parts[0].isdigit():
                    actual_numbers.append(int(parts[0]))
        
        assert len(actual_numbers) == len(expected_numbers)
    
    def test_find_replace_method(self):
        """Test find and replace method"""
        self.engine.add_files(self.test_files)
        
        self.engine.method = "replace"
        self.engine.find_text = "test_file"
        self.engine.replace_text = "renamed_file"
        plan = self.engine.generate_rename_plan()
        
        for original_path, new_name, matches in plan:
            if matches:
                assert "renamed_file" in new_name
                assert "test_file" not in new_name
    
    def test_conditions(self):
        """Test conditional filtering"""
        self.engine.add_files(self.test_files)
        
        # Test size condition
        self.engine.use_size_condition = True
        self.engine.size_operator = ">"
        self.engine.size_value = 0
        self.engine.size_unit = "Bytes"
        
        plan = self.engine.generate_rename_plan()
        matching_files = [p for p, n, m in plan if m]
        assert len(matching_files) > 0  # All files should match (size > 0)
        
        # Test impossible size condition
        self.engine.size_value = 999999
        self.engine.size_unit = "GB"
        plan = self.engine.generate_rename_plan()
        matching_files = [p for p, n, m in plan if m]
        assert len(matching_files) == 0  # No files should match
    
    def test_extension_condition(self):
        """Test extension filtering"""
        self.engine.add_files(self.test_files)
        
        self.engine.use_ext_condition = True
        self.engine.allowed_extensions = ".txt,.doc"
        
        plan = self.engine.generate_rename_plan()
        matching_files = [p for p, n, m in plan if m]
        assert len(matching_files) == len(self.test_files)  # All are .txt
        
        # Test non-matching extension
        self.engine.allowed_extensions = ".pdf,.doc"
        plan = self.engine.generate_rename_plan()
        matching_files = [p for p, n, m in plan if m]
        assert len(matching_files) == 0  # None are .pdf or .doc
    
    def test_transformations(self):
        """Test text transformations"""
        test_name = "Test File Name"
        
        # Test case transformations
        self.engine.case_method = "upper"
        result = self.engine.apply_transformations(test_name)
        assert result == "TEST FILE NAME"
        
        self.engine.case_method = "lower"
        result = self.engine.apply_transformations(test_name)
        assert result == "test file name"
        
        self.engine.case_method = "title"
        result = self.engine.apply_transformations(test_name)
        assert result == "Test File Name"
        
        # Test space replacement
        self.engine.case_method = "none"
        self.engine.replace_spaces = True
        result = self.engine.apply_transformations(test_name)
        assert result == "Test_File_Name"
        
        # Test special character removal
        self.engine.replace_spaces = False
        self.engine.remove_special_chars = True
        special_name = "Test@File#Name$"
        result = self.engine.apply_transformations(special_name)
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
    
    def test_duplicate_handling(self):
        """Test duplicate filename handling"""
        # Create files with same base name
        duplicate_files = []
        for i in range(2):
            test_file = self.temp_dir / f"duplicate.txt"
            if i == 1:
                test_file = self.temp_dir / f"duplicate_copy.txt"
            test_file.write_text(f"Content {i}")
            duplicate_files.append(str(test_file))
        
        self.engine.add_files(duplicate_files)
        self.engine.method = "replace"
        self.engine.find_text = "_copy"
        self.engine.replace_text = ""
        self.engine.handle_duplicates = True
        
        plan = self.engine.generate_rename_plan()
        new_names = [new_name for _, new_name, matches in plan if matches]
        
        # Should have unique names
        assert len(new_names) == len(set(new_names))


if __name__ == "__main__":
    pytest.main([__file__])