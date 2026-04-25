"""
Script to create a desktop shortcut for BookBot_07.
"""

import os
import winshell
from win32com.client import Dispatch

def create_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "BookBot 07.lnk")
    
    # Path to the batch file
    target = os.path.abspath(os.path.join(os.path.dirname(__file__), "run_bookbot.bat"))
    
    # Path to the icon
    icon = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "bookbot.ico"))
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = icon
    shortcut.save()
    
    print(f"Shortcut created on desktop: {path}")

if __name__ == "__main__":
    try:
        create_shortcut()
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        print("Make sure you have pywin32 and winshell installed.")
