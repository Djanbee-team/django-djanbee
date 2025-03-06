import unittest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import sys
import os

# Add the src directory to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)

# Now import directly from djanbee
from djanbee.managers.os_manager import OSManager


class TestSearchSubfolders(unittest.TestCase):
    def setUp(self):
        self.manager = OSManager()

    @patch("pathlib.Path.iterdir")
    @patch.object(OSManager, "get_dir")
    def test_finds_matches_in_current_directory(self, mock_get_dir, mock_iterdir):
        """Test that search_subfolders finds matching folders in current directory"""
        # Setup - use MagicMock instead of real Path
        mock_dir = MagicMock(spec=Path)
        mock_dir.name = "test"
        mock_get_dir.return_value = mock_dir

        # Create mock directories
        mock_dir1 = MagicMock(spec=Path)
        mock_dir1.name = "django_project"

        mock_dir2 = MagicMock(spec=Path)
        mock_dir2.name = "not"

        # Configure iterdir to return our mock dirs
        mock_iterdir.return_value = [mock_dir1, mock_dir2]

        # Create a validator function
        def validator(path):
            if "django" in path.name:
                return path.name
            return False

        # Call the method
        results = self.manager.search_subfolders(validator)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "django_project")  # Name
        self.assertEqual(results[0][1], mock_dir1)  # Path
        self.assertEqual(results[0][2], "django_project")  # Result value

        # Verify method calls
        mock_get_dir.assert_called_once()
        mock_iterdir.assert_called_once()


if __name__ == "__main__":
    unittest.main()
