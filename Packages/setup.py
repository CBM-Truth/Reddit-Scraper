from cx_Freeze import setup, Executable
import sys, os

sys.argv.append('build_exe')

base = None

executables = [Executable("main.py", base=base)]

packages = ["idna","praw","os","time",
            "sys","urllib.request","urllib","ctypes"]
            
options = {
    'build_exe': {
        'packages': packages,
    },

}

setup(
    options = options,
    version = "0.2",
    description = 'Reddit Scraper',
    executables = executables
)
