from cx_Freeze import setup, Executable
import sys
import os

os.environ['TCL_LIBRARY'] = 'C:\\Users\\camer\\AppData\Local\\Programs\\Python\\Python36\\tcl\\tcl8.6'
os.environ['TK_LIBRARY'] = 'C:\\Users\\camer\\AppData\Local\\Programs\\Python\\Python36\\tcl\\tk8.6'

sys.argv.append('build_exe')

base = None

executables = [Executable("scraper.py", base=base)]

packages = ["idna", "praw", "os", "time",
            "sys", "urllib.request", "ctypes", "shutil"]
            
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    options=options,
    version="0.3",
    description='Reddit Scraper',
    executables=executables
)
