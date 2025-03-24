import os
from unittest.mock import patch
from src.utils.get_path_of_files_modified_in_last_day import get_path_of_files_modified_in_last_day
from datetime import datetime, timedelta

class TestGetPathOfFilesModifiedInLastDay:

    def setup_method(self):
        self.mock_path = "fake_directory/pdfs"
        self.now = datetime.now()
    
    def test_files_modified_within_last_day(self):
        """
        Test that files modified within the last day are returned
        """
        mock_files = [
            (self.mock_path, [], ["file1.pdf", "file2.pdf", "file3.pdf"]),
        ]

        file_timestamps = {
            os.path.join(self.mock_path, "file1.pdf"): (self.now - timedelta(hours=1)).timestamp(),
            os.path.join(self.mock_path, "file2.pdf"): (self.now - timedelta(days=3)).timestamp(),
            os.path.join(self.mock_path, "file3.pdf"): (self.now - timedelta(hours=5)).timestamp()
        }

        with patch('os.walk', return_value=mock_files):
            with patch('os.path.getmtime', side_effect=lambda path: file_timestamps[path]):
                result = get_path_of_files_modified_in_last_day(self.mock_path)
        
        assert result == [
            os.path.join(self.mock_path, "file1.pdf"),
            os.path.join(self.mock_path, "file3.pdf")
        ]

    def test_no_files(self):
        """
        Test that an empty list is returned when there are no files in the directory
        """
        mock_files = []

        with patch('os.walk', return_value=mock_files):
            result = get_path_of_files_modified_in_last_day(self.mock_path)
        assert result == []
