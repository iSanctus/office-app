# build_exe.py
"""
Script to build ZisCRM executable
Run this script to create a standalone .exe file
"""

import os
import sys
import subprocess
import shutil

def clean_build_folders():
    """Remove old build folders"""
    folders_to_remove = ['build', 'dist']
    for folder in folders_to_remove:
        if os.path.exists(folder):
            print(f"Removing old {folder} folder...")
            shutil.rmtree(folder)

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n" + "="*50)
    print("Building ZisCRM Executable")
    print("="*50 + "\n")

    # Check if logo.ico exists
    if not os.path.exists('logo.ico'):
        print("WARNING: logo.ico not found! Building without icon.")
        icon_param = ''
    else:
        icon_param = '--icon=logo.ico'

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=ZisCRM',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
    ]

    if icon_param:
        cmd.append(icon_param)

    cmd.extend([
        '--add-data=database.py;.',
        '--add-data=receipt_generator.py;.',
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.pdfbase',
        '--hidden-import=reportlab.pdfbase.ttfonts',
        '--hidden-import=reportlab.pdfgen.canvas',
        '--hidden-import=openpyxl',
        '--hidden-import=sqlite3',
        '--collect-all=customtkinter',
        '--collect-all=reportlab',
        'app.py'
    ])

    print("Running PyInstaller...")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "="*50)
        print("✅ Build Successful!")
        print("="*50)
        print(f"\nYour executable is located at: dist/ZisCRM.exe")
        print("\nIMPORTANT NOTES:")
        print("1. The database will be created automatically on first run")
        print("2. Make sure to include any logo/signature images separately")
        print("3. The app will create 'attachments' folder automatically")
        print("4. For Greek fonts in PDF, ensure Arial is available on target systems")
        print("\nNetwork Database Location:")
        print("   Currently set to: \\\\MYCLOUDEX2ULTRA\\documentszis\\Τα έγγραφά μου\\CRM")
        print("   Change SHARED_PATH in database.py if needed before building")
    else:
        print("\n❌ Build Failed!")
        print("Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    print("ZisCRM - Executable Builder")
    print("============================\n")

    # Step 1: Clean old builds
    clean_build_folders()

    # Step 2: Install PyInstaller
    install_pyinstaller()

    # Step 3: Build
    build_executable()

    print("\nBuild process completed!")
