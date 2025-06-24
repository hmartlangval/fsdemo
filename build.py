"""Build script to create executable for test_fiserv_demo.py"""
import PyInstaller.__main__
import os

def build_executable():
    """Build the executable using PyInstaller"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to test_fiserv_demo.py
    script_path = os.path.join(current_dir, 'test_fiserv_demo.py')
    
    # Define PyInstaller arguments
    args = [
        script_path,  # Script to build
        '--onefile',  # Create a single executable
        '--name=fiserv_demo',  # Name of the output executable
        '--noconsole',  # Don't show console window
        # Add required hidden imports
        '--hidden-import=selenium',
        '--hidden-import=appium',
        '--hidden-import=appium.webdriver',
        '--hidden-import=appium.webdriver.common.mobileby',
        # Add the windows_automation.py as data file
        '--add-data={}{}windows_automation.py;.'.format(current_dir, os.sep),
    ]
    
    print("Starting build process...")
    PyInstaller.__main__.run(args)
    print("Build complete! Check the 'dist' folder for the executable.")

if __name__ == "__main__":
    build_executable() 