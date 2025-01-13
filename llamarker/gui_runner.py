# llamarker/gui_runner.py
import subprocess
import sys
import os

def main():
    gui_path = os.path.join(os.path.dirname(__file__), "llamarker_gui.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", gui_path])
