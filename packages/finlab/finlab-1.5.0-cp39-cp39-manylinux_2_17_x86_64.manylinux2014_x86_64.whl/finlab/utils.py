import os
import sys
import logging
import urllib3
import requests
from pathlib import Path

import finlab

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get an instance of a logger
logger = logging.getLogger(__name__)


def read_resource_file(package, resource):
    try:
        # For Python 3.9 and later
        from importlib.resources import files
        resource_path = files(package) / resource
        with open(resource_path, encoding='utf-8') as file:
            return file.read()
    except ImportError:
        try:
            # For Python 3.7 and 3.8
            from importlib.resources import path
            with path(package, resource) as resource_path:
                with open(resource_path, encoding='utf-8') as file:
                    return file.read()
        except ImportError:
            # Fallback for older Python versions without importlib.resources
            import pkg_resources
            resource_path = pkg_resources.resource_filename(package, resource)
            with open(resource_path, encoding='utf-8') as file:
                return file.read()
    raise ImportError("No compatible importlib.resources implementation found.")


def get_tmp_dir():
    # Check if running in Google Colab
    if 'COLAB_GPU' in os.environ:
        # Try to use Google Drive as the tmp directory
        try:
            # Mount Google Drive
            # from google.colab import drive
            if os.path.exists('/content/drive/'):
                default_path = "/content/drive/My Drive/Colab_tmp/finlab_db"
                logger.info("Google Drive is mounted. Using Google Drive as data directory.")
                # drive.mount('/content/drive')
            else:
                default_path = "/content/finlab_db"
                logger.info("Tip: Link to Google Drive as data storage so that "
                            "you can access the data without downloading it again.")

            # Custom tmp dir inside Google Drive
            google_drive_tmp_dir = Path(default_path)
            google_drive_tmp_dir.mkdir(parents=True, exist_ok=True)

            return str(google_drive_tmp_dir)

        except ImportError:
            print("Google Drive is not mounted. Please mount Google Drive to use as tmp directory.")
            raise

    # If running in a cloud function environment
    elif os.environ.get('FUNCTION_TARGET', None):
        # Set tmp directory to be /tmp for cloud functions
        tmp_subdir = Path("/tmp/finlab_db")
        tmp_subdir.mkdir(parents=True, exist_ok=True)
        return str(tmp_subdir)


    # For local machine use-cases
    else:
        # Default tmp directory
        home_dir = Path.home()

        # Create 'finlab_db' under tmp directory
        tmp_subdir = Path(home_dir) / 'finlab_db'
        tmp_subdir.mkdir(parents=True, exist_ok=True)

        return str(tmp_subdir)


def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        data = response.json()
        return data['info']['version']
    except:
        return '?'


def check_version_function_factory():

    """ Check finlab package version is the latest or not

    if the package version is out of date, info user to update.

    Returns
        None

    """
    if "pyodide" in sys.modules:
        return lambda : None

    latest_package_version = None

    def ret():

        nonlocal latest_package_version

        if latest_package_version is None:
            latest_package_version = get_latest_version('finlab')

            if latest_package_version != finlab.__version__ and latest_package_version != '?':
                logger.warning(f'Your version is {finlab.__version__}, please install a newer version.\nUse "pip install finlab=={latest_package_version}" to update the latest version.')

    return ret


def global_object_getter_setter_factory():
    _finlab_global_objects = {}

    def get_global(name):
        nonlocal _finlab_global_objects
        if name in _finlab_global_objects:
            return _finlab_global_objects[name]
        else:
            return None

    def set_global(name, obj):
        nonlocal _finlab_global_objects
        _finlab_global_objects[name] = obj
        if "pyodide" in sys.modules and "js" in sys.modules:
            import js
            from pyodide import ffi
            if hasattr(js, "_pyodide_execution_id"):
                js.postMessage(ffi.to_js({'content': obj, 'finish': False, 'type': name, 'id': js._pyodide_execution_id}))


    return get_global, set_global

def notify_progress(snippet_id, position, progress):
    """  notify progress of the backtest (only work in pyodide)
    """

    if "pyodide" in sys.modules and "js" in sys.modules:
        import js
        from pyodide import ffi
        if hasattr(js, "_pyodide_execution_id"):
            content = {
                "nstocks": (position!=0).sum(axis=1).mean(),
                "timestamp": snippet_id,
                "progress": progress,
            }

            js.postMessage(ffi.to_js({'content': content, 'finish': False, 'type': "backtest-progress", 'id': js._pyodide_execution_id}))


get_global, set_global = global_object_getter_setter_factory()
check_version = check_version_function_factory()
