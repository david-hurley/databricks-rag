import os
from datetime import datetime, timedelta

def get_path_of_files_modified_in_last_day(path_to_file):
    """
    Retrieves the paths of files in the specified directory (and its subdirectories)
    that were modified within the last 24 hours.

    Args:
        path_to_file (str): The root directory path to search for files.

    Returns:
        list[str]: A list of file paths that were modified within the last 24 hours.
    """

    files_modified_last_day = []

    one_day_ago = datetime.now() - timedelta(days=1)

    files = [os.path.join(root, file) for root, _, files in os.walk(path_to_file) for file in files]

    files_modified_last_day.extend(file for file in files if datetime.fromtimestamp(os.path.getmtime(file)) > one_day_ago)
                
    return files_modified_last_day

