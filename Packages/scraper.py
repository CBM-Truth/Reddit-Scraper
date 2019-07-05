import urllib.request as web
import ctypes as c 
import praw
import os
import shutil
import os.path
import sys
import time

SCREEN_WIDTH = c.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = c.windll.user32.GetSystemMetrics(1)
MAX_FILENAME_LENGTH = 170
MIN_FILE_SIZE = 300
DIRECTORY_FILE = 'dir.txt'
DEFAULT_CLIENT_ID = 'TB0-ZpHZQF6Qog'
DEFAULT_CLIENT_SECRET = 'Rz4XNGcDBZVMQE45IpB0EBl-p3s'
DEFAULT_USER_AGENT = 'windows:cbm.projects.redditscraper:v2.0 (by /u/PTTruTH)'


class Scraper:
    """
    Reddit Scraper Object
    """

    def __init__(self, client_id=DEFAULT_CLIENT_ID, client_secret=DEFAULT_CLIENT_SECRET,
                 user_agent=DEFAULT_USER_AGENT):
        self.__target_directory = self.__load_target_directory()
        self.__current_directory = os.getcwd()
        self.__reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def __load_target_directory(self):
        """
        If there is no file present containing a target location, a new file is made
        and the path is written. Will read the path from the file and update the
        target path
        :return: Target directory
        """
        if not os.path.exists(DIRECTORY_FILE):
            directory = input('Please enter a destination directory: ')
            self.__create_target_directory(directory)
        with open(DIRECTORY_FILE) as f:
            path = f.read()
            f.close()
        return path

    @staticmethod
    def __create_target_directory(directory):
        """
        Writes directory to a new text file named 'dir.txt'
        :param directory: directory to store scraped images
        """
        with open(DIRECTORY_FILE, 'w') as f:
            f.write(directory)
            f.close()

    @staticmethod
    def __log(subs, dls, errs):
        """
        Writes information about current execution to a log file
        :param subs: subreddits scraped
        :param dls: number of downloads
        :param errs: number of errors encountered
        """
        mode = 'w' if not os.path.exists('log.txt') else 'a'
        subs = subs.replace(' ', '')
        reddits = subs.replace(',', ', ')
        current_time = time.asctime(time.localtime(time.time()))
        with open('log.txt', mode) as f:
            f.write(current_time + '\n')
            f.write('Subreddits searched: ' + str(reddits) + '\n')
            f.write('Images downloaded: ' + str(dls) + '\n')
            f.write('Encountered errors: ' + errs + '\n')
            f.write('--------------------------------\n')
            f.close()

    @staticmethod
    def __is_digit(s):
        """
        Returns true if argument is of the float class, false otherwise
        :return: true if argument can be casted to a float, false otherwise
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def __get_resolution(self, title):
        """
        Returns the resolution embedded in a reddit post title of the form: (width, height)
        :param title: Title string of the reddit post
        :return: Resolution of the image in the post as specified by the OP
        """
        res = ''
        for char in filter(lambda char: char in title, ['[', ']', '(', ')']):
            title = title.replace(char, '')
        title = list(title)

        for char in title:
            if self.__is_digit(char):
                res += 'x' + char if len(res) == 4 else char
        res = res.split('x')
        if len(res) < 2:
            return 0, 0

        width, height = res[0], res[1]
        if len(width) < 4 or len(height) < 4:
            width, height = 0, 0
        return int(width), int(height)

    def __compatible(self, post):
        """
        Returns true if the resolution in the post title is at least 1920x1080 and if width > height
        returns false otherwise
        :param post:
        :return:
        """
        width, height = self.__get_resolution(post.title)
        good_domain = "i.redd.it" in post.domain or "imgur" in post.domain
        on_disk = os.path.exists(os.path.join(self.__target_directory, self.__cleanup_title(post.title)))
        correct_dimensions = width >= SCREEN_WIDTH and width > height >= SCREEN_HEIGHT
        return correct_dimensions and good_domain and not on_disk

    @staticmethod
    def __cleanup_title(string):
        """
        Removes bad characters from and appends '.jpg' to end of string
        :param string: string to be modified
        :return: modified string
        """
        chars = ['/', '\\', ':', '*', '?', '<', '>', '"', '|']
        for char in filter(lambda char: char in string, chars):
            string = string.replace(char, '')
        return string + '.jpg'

    @staticmethod
    def __cleanup_url(url):
        """
        Appends '.jpg' the image url if it isn't already present, returns a new string
        :param url: url to modify
        :return: modified url
        """
        ret_str = url
        url = url.split('.')
        if url[-1] != 'jpg':
            ret_str += '.jpg'
        return ret_str

    @staticmethod
    def __size_filter(directory):
        """
        Removes files < 300KB from the argument directory
        :return: number of files removed as an integer
        """
        dels = 0
        for subdir in os.listdir(directory):
            _file = os.path.join(directory, subdir)
            if os.path.getsize(_file) / 1000 < MIN_FILE_SIZE:
                os.remove(_file)
                dels += 1
        return dels

    def scrape(self, subreddits, _max):
        """
        Downloads all compatible images from the passed subreddits, searches for a max of _max from
        each subreddit. All images are placed in the target_path destination at the end of runtime
        :param subreddits: array of subreddit name strings
        :param _max: maximum number of posts to scrape
        """
        errors = 0
        downloads = 0
        print('Detected Resolution: [{}x{}]'.format(str(SCREEN_WIDTH), str(SCREEN_HEIGHT)))

        subs = [sub + 'porn' if 'porn' not in sub else sub
                for sub in subreddits.replace(' ', '').split(',')]

        compatible_posts = [post for sub in subs for post in self.__reddit.subreddit(sub).hot(limit=int(_max))
                            if self.__compatible(post)]

        if len(compatible_posts) == 0:
            print('No compatible images found')
            print('Exiting...')
            sys.exit()

        print('{} compatible images detected'.format(str(len(compatible_posts))))
        print('Collecting images...\n')
        time.sleep(1)

        for post in compatible_posts:
            filename = self.__cleanup_title(post.title)
            if len(filename) >= MAX_FILENAME_LENGTH:
                print('Image name is too long, renaming file...')
                m = int(len(filename) / 2)
                filename = filename[:m] + '.jpg'
            stored_file = os.path.join(self.__target_directory, filename)
            raw_file = os.path.join(self.__current_directory, filename)
            _file = open(filename, 'wb')

            try:
                _file.write(web.urlopen(self.__cleanup_url(post.url)).read())
                _file.close()
                shutil.move(raw_file, stored_file)
                downloads += 1
                print(filename.encode('ascii', 'ignore').decode() + ' (' + str(post.ups) + ' upvote(s)) written')
            except Exception as e:
                print(str(e))
                print('Unable to write file: ' + filename + ' (' + post.url + ')')
                _file.close()
                os.remove(raw_file)
                errors += 1

        dels = self.__size_filter(self.__target_directory)
        new_download_count = downloads - dels
        print('\n' + str(new_download_count) + ' new image(s) downloaded')

        if dels > 0:
            print('{} image(s) smaller than {}KB removed'.format(str(dels), str(MIN_FILE_SIZE)))

        errors = 'Failed to download {} images'.format(str(errors))
        print(errors)
        print('Opening image directory and exiting...')
        self.__log(subreddits, new_download_count, errors)
        time.sleep(2)
        os.startfile(self.__target_directory)


if __name__ == '__main__':
    subs = input("Enter subreddit(s) to pull images from separated by commas: ")
    search_limit = input("Enter number of images to scan from each subreddit: ")

    scraper = Scraper()
    scraper.scrape(subs, search_limit)






 


    
    

                     
