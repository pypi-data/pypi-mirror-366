import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from universal_printer import DocumentPrinter


class TestDocumentPrinter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.printer = DocumentPrinter()
        self.test_content = "This is a test document.\nWith multiple lines.\nFor testing purposes."
    
    def test_init(self):
        """Test DocumentPrinter initialization."""
        self.assertIsInstance(self.printer, DocumentPrinter)
        self.assertIsNotNone(self.printer.system)
        self.assertIsInstance(self.printer.downloads_path, Path)
    
    def test_write_temp_text(self):
        """Test temporary text file creation."""
        temp_path = self.printer._write_temp_text(self.test_content)
        
        # Check that file was created
        self.assertTrue(temp_path.exists())
        self.assertTrue(temp_path.suffix == '.txt')
        
        # Check content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, self.test_content)
        
        # Clean up
        temp_path.unlink()
    
    def test_write_minimal_pdf(self):
        """Test minimal PDF generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "test.pdf"
            
            success = self.printer._write_minimal_pdf(self.test_content, pdf_path)
            
            self.assertTrue(success)
            self.assertTrue(pdf_path.exists())
            
            # Check that it's a valid PDF (starts with PDF header)
            with open(pdf_path, 'rb') as f:
                header = f.read(8)
            self.assertTrue(header.startswith(b'%PDF-1.4'))
    
    def test_fallback_pdf_save(self):
        """Test PDF fallback functionality."""
        # Test with default filename
        pdf_path = self.printer._fallback_pdf_save(self.test_content)
        
        self.assertIsNotNone(pdf_path)
        self.assertTrue(Path(pdf_path).exists())
        self.assertTrue(str(pdf_path).endswith('.pdf'))
        
        # Clean up
        Path(pdf_path).unlink()
        
        # Test with custom filename
        custom_filename = "custom_test_file"
        pdf_path = self.printer._fallback_pdf_save(self.test_content, custom_filename)
        
        self.assertIsNotNone(pdf_path)
        self.assertTrue(Path(pdf_path).exists())
        self.assertTrue(str(pdf_path).endswith('.pdf'))
        self.assertIn('custom_test_file', str(pdf_path))
        
        # Clean up
        Path(pdf_path).unlink()
    
    def test_print_document_with_fallback(self):
        """Test print_document with PDF fallback enabled."""
        # This test will likely fail to print (no printer configured in test environment)
        # but should succeed with PDF fallback
        success, message, pdf_path = self.printer.print_document(
            self.test_content, 
            fallback_to_pdf=True,
            pdf_filename="test_fallback"
        )
        
        # In test environment, printing will likely fail but PDF should be created
        if not success and pdf_path:
            self.assertIsNotNone(pdf_path)
            self.assertTrue(Path(pdf_path).exists())
            # Clean up
            Path(pdf_path).unlink()
        
        # The test passes if either printing succeeded OR PDF fallback worked
        self.assertTrue(success or pdf_path is not None)
    
    def test_print_document_no_fallback(self):
        """Test print_document with PDF fallback disabled."""
        success, message, pdf_path = self.printer.print_document(
            self.test_content, 
            fallback_to_pdf=False
        )
        
        # With fallback disabled, pdf_path should be None if printing fails
        if not success:
            self.assertIsNone(pdf_path)
    
    def test_print_existing_file(self):
        """Test printing an existing file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_content)
            temp_file_path = f.name
        
        try:
            success, message, pdf_path = self.printer.print_document(
                temp_file_path, 
                fallback_to_pdf=True
            )
            
            # Should handle the file path correctly
            self.assertIsInstance(success, bool)
            self.assertIsInstance(message, str)
            
            # Clean up PDF if created
            if pdf_path and Path(pdf_path).exists():
                Path(pdf_path).unlink()
                
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
    
    def test_system_detection(self):
        """Test that system is properly detected."""
        system = self.printer.system
        self.assertIn(system, ['Windows', 'Darwin', 'Linux'])
    
    def test_downloads_path(self):
        """Test downloads path is set correctly."""
        downloads_path = self.printer.downloads_path
        self.assertIsInstance(downloads_path, Path)
        # Should be user's home directory + Downloads
        expected_path = Path.home() / "Downloads"
        self.assertEqual(downloads_path, expected_path)


if __name__ == '__main__':
    unittest.main()