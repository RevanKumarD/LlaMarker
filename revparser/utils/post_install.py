import subprocess
import sys

def install_marker():
    """Install the Marker package from GitHub."""
    try:
        print("Installing marker from GitHub...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "git+https://github.com/VikParuchuri/marker.git"
        ])
        print("Marker installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing marker: {e}")
        raise RuntimeError("Failed to install 'marker'. Please install it manually.")
