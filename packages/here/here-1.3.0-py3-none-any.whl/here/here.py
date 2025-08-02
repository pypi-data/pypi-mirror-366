from pathlib import Path
from IPython import get_ipython


def get_root_directory(print_debug_info=False):
    """
    Determines the root directory based on the execution environment.

    - If running in a Jupyter notebook, returns the current working directory.
    - Otherwise, returns the directory of the script containing this function.

    Args:
        print_debug_info (bool): If True, prints debug information.

    Returns:
        str: The root directory.
    """
    # Check if running in a Jupyter notebook
    if get_ipython() is not None and hasattr(get_ipython(), "config"):
        if print_debug_info:
            print("Debug Info: Running in a Jupyter notebook. Returning current working directory.")
        return str(Path.cwd())

    # Return the directory of this script
    root_directory = str(Path(__file__).parent)
    if print_debug_info:
        print(f"Debug Info: Returning the directory of this script: {root_directory}")
    return root_directory


def here(path="", print_debug_info=False):
    """
    Resolves a path relative to the root directory.

    Args:
        path (str): A string representing the relative path to resolve.
        print_debug_info (bool): If True, prints debug information.

    Returns:
        str: The resolved full path.
    """
    root_directory = Path(get_root_directory(print_debug_info))
    resolved_path = root_directory.joinpath(*path.split("/")).resolve()
    if print_debug_info:
        print(f"Debug Info: Resolving path '{path}' relative to root directory '{root_directory}'.")
        print(f"Debug Info: Resolved path is '{resolved_path}'.")
    return str(resolved_path)


if __name__ == "__main__":
    # Example usage
    print("File Working Directory:", get_root_directory())
    print("Resolved Path of subfolders data/output:", here("data/output"))
    print("Resolved Path with config folder parallel to Parent:", here("../config"))
