import sys
from site import getsitepackages
import os


def get_source_root():
    return os.path.realpath(os.path.dirname(__file__))


def get_app_data_path(subdir=None):
    """
    Retrieve the venv or OS's directory for mutuable app data (translations or config).
    """
    app = 'berea'
    
    # Check if a virtual environment is active
    if hasattr(sys, 'prefix') and sys.prefix != sys.base_prefix:
        # Get path to venv/lib/python3.XX/site-packages/
        venv_site_packages = getsitepackages()[0]
        path = os.path.join(venv_site_packages, app)
    
    # No venv, use OS's standard path for config
    else:
        system_platform = sys.platform
        
        if system_platform == 'win32':
            path = os.path.join(os.environ.get('APPDATA', ''), app)
        elif system_platform == 'darwin':  # macOS
            path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app)
        elif system_platform == 'linux':
            path = os.path.join(os.path.expanduser('~'), '.config', app)
        
        else:
            sys.exit(f"Unsupported platform: {system_platform}")
    
    if subdir:
            path = os.path.join(path, subdir)
    
    # Create berea directory if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
        
    return path


def get_downloaded_translations():
    translations_path = get_app_data_path('translations')
    
    if os.path.exists(translations_path):
        files = os.listdir(translations_path)
        
        downloaded_translations = []
        
        for file in files:
            if file.endswith('.db'):
                downloaded_translations.append(file[:-3])
        
        return sorted(downloaded_translations)
