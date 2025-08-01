# unit tests for ntparse core functionality

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from ntparse.core import (
    get_syscalls, 
    parse_ntdll, 
    validate_ntdll_path,
    NtParseError
)
from ntparse.utils import (
    detect_system_architecture,
    get_default_ntdll_path,
    is_valid_ntdll,
    get_exported_functions
)


class TestCoreFunctions:
    """Test core parsing functions"""
    
    def test_get_syscalls_file_not_found(self):
        """Test get_syscalls with non-existent file"""
        with pytest.raises(NtParseError, match="File not found"):
            get_syscalls("nonexistent.dll")
    
    @patch('ntparse.core.pefile.PE')
    def test_get_syscalls_no_exports(self, mock_pe):
        """Test get_syscalls with PE file that has no exports"""
        # Mock PE file without exports
        mock_pe_instance = MagicMock()
        mock_pe_instance.DIRECTORY_ENTRY_EXPORT = None
        mock_pe.return_value = mock_pe_instance
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake dll content')
            temp_path = f.name
        
        try:
            with pytest.raises(NtParseError, match="No export directory found"):
                get_syscalls(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('ntparse.core.capstone.Cs')
    def test_get_syscalls_capstone_error(self, mock_capstone):
        """Test get_syscalls with capstone initialization error"""
        mock_capstone.side_effect = Exception("Capstone error")
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake dll content')
            temp_path = f.name
        
        try:
            with pytest.raises(NtParseError, match="Failed to initialize capstone"):
                get_syscalls(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_parse_ntdll_unsupported_arch(self):
        """Test parse_ntdll with unsupported architecture"""
        with pytest.raises(NtParseError, match="Currently only x64 architecture is supported"):
            parse_ntdll(arch="x86")
    
    @patch('ntparse.core.get_syscalls')
    def test_parse_ntdll_default_path(self, mock_get_syscalls):
        """Test parse_ntdll with default path"""
        mock_get_syscalls.return_value = {"NtClose": 0x0C}
        
        result = parse_ntdll()
        
        assert result == {"NtClose": 0x0C}
        mock_get_syscalls.assert_called_once()
        # Check that it was called with a path containing ntdll.dll
        call_args = mock_get_syscalls.call_args[0][0]
        assert "ntdll.dll" in str(call_args)
    
    @patch('ntparse.core.get_syscalls')
    def test_parse_ntdll_custom_path(self, mock_get_syscalls):
        """Test parse_ntdll with custom path"""
        mock_get_syscalls.return_value = {"NtOpenProcess": 0x26}
        
        result = parse_ntdll("C:\\custom\\ntdll.dll")
        
        assert result == {"NtOpenProcess": 0x26}
        mock_get_syscalls.assert_called_once_with("C:\\custom\\ntdll.dll")
    
    def test_validate_ntdll_path_nonexistent(self):
        """Test validate_ntdll_path with non-existent file"""
        assert not validate_ntdll_path("nonexistent.dll")
    
    @patch('ntparse.core.pefile.PE')
    def test_validate_ntdll_path_invalid_pe(self, mock_pe):
        """Test validate_ntdll_path with invalid PE file"""
        mock_pe.side_effect = Exception("Invalid PE")
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake content')
            temp_path = f.name
        
        try:
            assert not validate_ntdll_path(temp_path)
        finally:
            os.unlink(temp_path)


class TestUtilsFunctions:
    """Test utility functions"""
    
    def test_detect_system_architecture(self):
        """Test system architecture detection"""
        arch = detect_system_architecture()
        assert arch in ["x64", "x86"]
    
    def test_get_default_ntdll_path(self):
        """Test default ntdll path generation"""
        path = get_default_ntdll_path()
        assert "ntdll.dll" in path
        assert "System32" in path
    
    @patch('ntparse.utils.pefile.PE')
    def test_is_valid_ntdll_valid(self, mock_pe):
        """Test is_valid_ntdll with valid ntdll"""
        mock_pe_instance = MagicMock()
        mock_pe_instance.OPTIONAL_HEADER.Magic = 0x20b  # PE32+
        mock_pe_instance.FILE_HEADER.Characteristics = 0x2000  # DLL
        mock_pe_instance.DIRECTORY_ENTRY_EXPORT = MagicMock()
        mock_pe.return_value = mock_pe_instance
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake dll content')
            temp_path = f.name
        
        try:
            assert is_valid_ntdll(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('ntparse.utils.pefile.PE')
    def test_is_valid_ntdll_invalid(self, mock_pe):
        """Test is_valid_ntdll with invalid file"""
        mock_pe_instance = MagicMock()
        mock_pe_instance.OPTIONAL_HEADER.Magic = 0x10b  # PE32 (not PE32+)
        mock_pe.return_value = mock_pe_instance
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake dll content')
            temp_path = f.name
        
        try:
            assert not is_valid_ntdll(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('ntparse.utils.pefile.PE')
    def test_get_exported_functions(self, mock_pe):
        """Test get_exported_functions"""
        mock_pe_instance = MagicMock()
        mock_export = MagicMock()
        mock_export.name = b'NtClose'
        mock_pe_instance.DIRECTORY_ENTRY_EXPORT.symbols = [mock_export]
        mock_pe.return_value = mock_pe_instance
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake dll content')
            temp_path = f.name
        
        try:
            functions = get_exported_functions(temp_path)
            assert functions == ['NtClose']
        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_ntparse_error_inheritance(self):
        """Test that NtParseError inherits from Exception"""
        error = NtParseError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    @patch('ntparse.core.pefile.PE')
    def test_get_syscalls_pe_parse_error(self, mock_pe):
        """Test get_syscalls with PE parsing error"""
        mock_pe.side_effect = Exception("PE parsing failed")
        
        with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as f:
            f.write(b'fake dll content')
            temp_path = f.name
        
        try:
            with pytest.raises(NtParseError, match="Failed to parse PE file"):
                get_syscalls(temp_path)
        finally:
            os.unlink(temp_path) 