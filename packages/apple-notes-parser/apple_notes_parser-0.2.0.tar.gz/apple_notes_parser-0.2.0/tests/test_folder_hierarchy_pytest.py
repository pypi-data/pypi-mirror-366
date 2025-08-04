"""
Pytest tests for folder hierarchy functionality.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_notes_parser.database import AppleNotesDatabase


def test_folder_parent_extraction(test_database):
    """Test that folder parent IDs are extracted correctly."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        # Check that we have the expected folders
        assert len(folders_list) == 6

        # Check specific parent relationships
        folders_by_name = {f.name: f for f in folders_list}

        # Root folder should have no parent
        assert folders_by_name["Notes"].parent_id is None
        assert folders_by_name["Notes"].is_root()

        # Folder2 should be a root folder (no parent)
        assert folders_by_name["Folder2"].parent_id is None
        assert folders_by_name["Folder2"].is_root()

        # Subfolder should have Folder2 as parent
        assert folders_by_name["Subfolder"].parent_id == folders_by_name["Folder2"].id
        assert not folders_by_name["Subfolder"].is_root()


def test_folder_path_construction(test_database):
    """Test that folder paths are constructed correctly."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        folders_by_name = {f.name: f for f in folders_list}

        # Test specific paths based on real database structure
        assert folders_by_name["Notes"].get_path() == "Notes"
        assert folders_by_name["Folder"].get_path() == "Folder"  # Top-level folder
        assert folders_by_name["Folder2"].get_path() == "Folder2"  # Top-level folder
        assert folders_by_name["Subfolder"].get_path() == "Folder2/Subfolder"
        assert (
            folders_by_name["Subsubfolder"].get_path()
            == "Folder2/Subfolder/Subsubfolder"
        )


def test_folder_parent_navigation(test_database):
    """Test folder parent navigation methods."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        folders_by_name = {f.name: f for f in folders_list}

        # Test parent navigation with real folder hierarchy
        subsubfolder = folders_by_name["Subsubfolder"]
        subfolder = subsubfolder.get_parent()
        assert subfolder.name == "Subfolder"

        folder2 = subfolder.get_parent()
        assert folder2.name == "Folder2"

        # Folder2 is a root folder, should have no parent
        assert folder2.get_parent() is None


def test_folder_path_without_dict(test_database):
    """Test folder path fallback when no folders_dict is provided."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        folders_by_name = {f.name: f for f in folders_list}

        # Without folders_dict, should just return the folder name
        # Without parent relationships, should just return the folder name
        # Create isolated folders to test fallback behavior
        isolated_folder = folders_by_name["Subsubfolder"]
        isolated_folder.parent = None  # Remove parent to test fallback
        assert isolated_folder.get_path() == "Subsubfolder"

        isolated_folder2 = folders_by_name["Folder2"]
        assert isolated_folder2.get_path() == "Folder2"


def test_parser_folder_integration(test_database):
    """Test folder hierarchy integration with direct database access."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)
        folders_dict = {folder.id: folder for folder in folders_list}

        assert len(folders_dict) == 6

        # Test that all folders have correct paths
        folders_by_name = {f.name: f for f in folders_list}

        paths = {
            "Notes": "Notes",
            "Folder": "Folder",
            "Folder2": "Folder2",
            "Subfolder": "Folder2/Subfolder",
            "Subsubfolder": "Folder2/Subfolder/Subsubfolder",
        }

        for name, expected_path in paths.items():
            actual_path = folders_by_name[name].get_path()
            assert actual_path == expected_path, (
                f"Expected {expected_path}, got {actual_path}"
            )


def test_export_includes_folder_paths(test_database):
    """Test that folder data includes path information."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        # Should have all 6 folders
        assert len(folders_list) == 6

        # Check specific folder paths
        folders_by_name = {f.name: f for f in folders_list}

        expected_paths = {
            "Notes": "Notes",
            "Folder": "Folder",
            "Folder2": "Folder2",
            "Subfolder": "Folder2/Subfolder",
            "Subsubfolder": "Folder2/Subfolder/Subsubfolder",
        }

        for name, expected_path in expected_paths.items():
            actual_path = folders_by_name[name].get_path()
            assert actual_path == expected_path
            # Also check parent_id is correctly set
            if name in ["Notes", "Recently Deleted", "Folder", "Folder2"]:
                # These are root folders
                assert folders_by_name[name].parent_id is None
            else:
                # These should have parents (Subfolder, Subsubfolder)
                assert folders_by_name[name].parent_id is not None


def test_root_folder_detection(test_database):
    """Test detection of root folders."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        root_folders = [f for f in folders_list if f.is_root()]
        # Should have multiple root folders: Notes, Recently Deleted, Folder, Folder2
        assert len(root_folders) == 4
        root_names = {f.name for f in root_folders}
        expected_root_names = {"Notes", "Recently Deleted", "Folder", "Folder2"}
        assert root_names == expected_root_names


def test_cycle_prevention(test_database):
    """Test that cycle detection prevents infinite loops."""
    with AppleNotesDatabase(test_database) as db:
        accounts_list = db.get_accounts()
        accounts_dict = {acc.id: acc for acc in accounts_list}
        folders_list = db.get_folders(accounts_dict)

        # Artificially create a cycle by making Notes point to itself
        notes_folder = next(f for f in folders_list if f.name == "Notes")
        notes_folder.parent_id = notes_folder.id  # Create cycle

        # Should not cause infinite loop, just return the folder name
        path = notes_folder.get_path()
        assert path == "Notes"
