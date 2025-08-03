import string
import os
import psutil
import sys
import platform
from ctypes import wintypes, WinDLL, c_wchar_p

def _load_dll():
    '''
    Load the dir_size.dll with proper path for PyPI distribution.
    '''
    
    dll_path = os.path.join(os.path.dirname(__file__), "dir_size.dll")
    
    if os.path.exists(dll_path):
        try:
            dll = WinDLL(dll_path)
            dll.get_directory_size.argtypes = [wintypes.LPCWSTR]
            dll.get_directory_size.restype = c_wchar_p
            return dll
        except Exception as e:
            raise RuntimeError(f"Failed to load DLL from {dll_path}: {e}")
    
    # If dll not found, provide error message
    raise FileNotFoundError(
        f"dir_size.dll not found at {dll_path}. "
        "Make sure the DLL is included in the package distribution."
    )

try:
    dir_size_dll = _load_dll()
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("This package requires dir_size.dll to function properly.")
    sys.exit(1)

def _should_calculate(item_path: str) -> bool:
    '''
    Determines if the size of a file or directory should be calculated.

    Args:
        item_path: The path to the file or directory.

    Returns:
        True if the size should be calculated, False otherwise.
    '''

    if not os.path.exists(item_path):
        return False

    def is_immediate_subdir_of_drive(path: str) -> bool:
        '''
        Checks if the given Windows path is an immediate subdirectory of a drive root.

        Args:
            path: The path to check.

        Returns:
            True if the path is an immediate subdirectory of a drive root, False otherwise.
        '''

        path = os.path.abspath(path)
        drive, tail = os.path.splitdrive(path)
        if not drive:
            return False  # Not a valid drive path

        # Normalize and split
        parts = os.path.normpath(path).split(os.sep)
        
        return len(parts) == 2 and parts[0].endswith(':')
    
    if is_immediate_subdir_of_drive(item_path) and os.path.isfile(item_path):
        return False

    if os.path.islink(item_path):
        return False
    
    # Inaccessible
    try:
        os.stat(item_path)
    except (PermissionError, FileNotFoundError, OSError):
        return False
    
    return True

def map_drives_to_sizes() -> dict:
    '''
    Returns a dictionary mapping drives to their sizes.

    Returns:
        A dictionary mapping drives to their sizes.
    '''

    drive_size_map = {}

    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"

        if os.path.exists(drive):
            try:
                # Get disk usage info
                usage = psutil.disk_usage(drive)
                size = usage.used
                drive_size_map[drive] = str(size)
            except (OSError, PermissionError):
                # Skip drives we can't access
                continue

    return drive_size_map

def map_children_to_sizes(dir_path: str) -> dict:   
    '''
    Returns a dictionary mapping subdir/file names to their sizes
    within the given directory.

    Args:
        dir_path: Path to the parent directory.

    Returns:
        A dict where keys are names of immediate children and values are their sizes.
    '''
    
    folder_size_map = {}

    for child_item in os.listdir(dir_path):
        child_item_path = os.path.join(dir_path, child_item)

        if not _should_calculate(child_item_path):
            continue

        child_item_size = dir_size_dll.get_directory_size(child_item_path)

        folder_size_map[child_item] = child_item_size

    return folder_size_map