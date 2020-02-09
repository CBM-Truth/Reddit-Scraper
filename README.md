# Reddit Scraper
Functional script that collects backgrounds images from photography subreddits like r/earthporn, r/spaceporn, r/skyporn, etc... 
The script will work with any subreddit where users put resolution information within post titles.
# Setup
All you need to run the script is the main.exe binary located within the \build\ parent directory. Clone the repository and extract the contents to a new folder. If you do not want access to the python files themselves, then delete everything inside your new folder except the build folder. 

Simply run main.exe located in build\exe.win-amd64-3.6\main.exe

The script will create two new text files when run for the first time: target_path.txt and log.txt. target_path.txt is used to store the path to the destination folder of your choice where all images will be saved. log.txt will be updated with meta information every time main.exe is executed.

The build file and all auxiliary libraries were create with cx_Freeze. I do not claim ownership of any IP within those libraries.