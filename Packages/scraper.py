import urllib.request as web
import ctypes as c 
import praw
import os
import os.path
import sys
import time
    
user = c.windll.user32
target_path = ''

SCREEN_WIDTH = user.GetSystemMetrics(0) 
SCREEN_HEIGHT = user.GetSystemMetrics(1)
CURRENT_PATH = os.getcwd()
MAX_FILENAME_LENGTH = 170


# post: If there is no file present containing a target location, a new file is made
# and the path is written. Will read the path from the file and return it as a string
def get_target_path():
    if not os.path.exists('target_path.txt'):
        target_path_input = input('Please enter a destination folder: ')
        create_target_path(target_path_input)
    with open('target_path.txt') as f:
        path = f.read()
        f.close()
    global target_path
    target_path = path


# post: Writes the path argument to a new text file named 'target_path.txt'
def create_target_path(path):
    with open('target_path.txt', 'w') as f:
        f.write(path)
        f.close()


# post: logs time of current execution to a log file on startup
def log(reddits, dls, errs):
    mode = 'w' if not os.path.exists('log.txt') else 'a'
    reddits = reddits.replace(' ', '')
    reddits = reddits.replace(',', ', ')
    current_time = time.asctime(time.localtime(time.time()))
    with open('log.txt', mode) as f:
        f.write(current_time + '\n')
        f.write('Subreddits searched: ' + str(reddits) + '\n')
        f.write('Images downloaded: ' + str(dls) + '\n')
        f.write('Encountered errors: ' + errs + '\n')
        f.write('--------------------------------\n')
        f.close()


# post: Returns true if argument is of the float class, false otherwise
def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# post: Returns the resolution embedded in a reddit post title in (width, height) form
def get_resolution(title):
    delims = ['[', ']', '(', ')']
    width, height = '', ''
    res = []
    for char in delims:
        if char in title:
            title = title.replace(char, '')
    title = list(title)
    for i in range(len(title)):
        if is_float(title[i]) and i >= int(len(title) * 0.6):
            res.append(title[i])
    mid = int(len(res) / 2)
    for element in res[:mid]:
        width += element
    for element in res[mid:]:
        height += element
    if len(width) == 0 or len(height) == 0:
            width, height = 0, 0
    return int(width), int(height)


# post: Returns true if the resolution in the post title is at least 1920x1080 and if width > height
# returns false otherwise
def compatible(post):
    width, height = get_resolution(post.title)
    good_domain = "i.redd.it" in post.domain or "imgur" in post.domain
    on_disk = os.path.exists(os.path.join(target_path, cleanup_title(post.title)))
    correct_dimensions = width >= SCREEN_WIDTH and width > height >= SCREEN_HEIGHT
    return correct_dimensions and good_domain and not on_disk


# post: removes problematic characters from a reddit post title for parsing,
# returns a new cleaned up string
def cleanup_title(text):
    chars = ['/', '\\', ':', '*', '?', '<', '>', '"', '|']
    for char in chars:
        if char in text:
            text = text.replace(char, '')
    return text + '.jpg'


# post: appends .jpg the image url if it isn't already present, returns a new string
def cleanup_url(url):
    ret_str = url
    url = url.split('.')
    if url[len(url) - 1] != 'jpg':
            ret_str += '.jpg'
    return ret_str

"""
post: removes files < 300KB from the argument path. Returns the number of files removed
as an integer
"""
def size_filter(main_path):
    dels = 0
    for sub_path in os.listdir(main_path):
        _file = os.path.join(main_path, sub_path)
        if os.path.getsize(_file) / 1000 < 300:
            os.remove(_file)
            dels += 1
    return dels


def get_images(subreddits, _max):
    """
    Downloads all compatible images from the passed subreddits, searches for a max of _max from
    each subreddit. All images are placed in the target_path destination at the end of runtime
    :param subreddits: array of subreddit name strings
    :param _max: maximum number of posts to scrape
    """

    get_target_path()
    errors = 0
    downloads = 0
    reddit = praw.Reddit(
             client_id='TB0-ZpHZQF6Qog',
             client_secret='Rz4XNGcDBZVMQE45IpB0EBl-p3s',
             user_agent='windows:cbm.projects.redditscraper:v2.0 (by /u/PTTruTH)'
             )
    print('Detected Resolution: [{}x{}]'.format(str(SCREEN_WIDTH), str(SCREEN_HEIGHT)))

    subs = [sub + 'porn' if 'porn' not in sub else sub
            for sub in subreddits.replace(' ', '').split(',')]

    compatible_posts = [post for sub in subs for post in reddit.subreddit(sub).hot(limit=int(_max))
                        if compatible(post)]

    if len(compatible_posts) == 0:
        print('No compatible images found')
        print('Exiting...')
        sys.exit()

    print(str(len(compatible_posts)) + ' compatible images detected')
    print('Collecting images...\n')
    time.sleep(1)

    for post in compatible_posts:
        filename = cleanup_title(post.title)
        if len(filename) >= MAX_FILENAME_LENGTH:
            print('Image name is too long, renaming file...')
            mid = int(len(filename) / 2)
            filename = filename[:mid] + '.jpg'
        stored_file = os.path.join(target_path, filename)
        raw_file = os.path.join(CURRENT_PATH, filename)
        _file = open(filename, 'wb')
        try:
            _file.write(web.urlopen(cleanup_url(post.url)).read())
            _file.close()
            os.rename(raw_file, stored_file)
            downloads += 1
        except Exception as e:
            print(str(e))
            print('Unable to write file: ' + filename + ' (' + post.url + ')')
            _file.close()
            os.remove(raw_file)
            errors += 1
        print(filename.encode('ascii', 'ignore').decode() + ' (' + str(post.ups) + ' upvote(s)) written')

    dels = size_filter(target_path)
    new_download_count = downloads - dels
    print('\n' + str(new_download_count) + ' new image(s) downloaded')

    if dels > 0:
        print(str(dels) + ' image(s) smaller than 300KB removed')

    errors = 'HTTP Errors: {}'.format(str(errors))
    print(errors)
    print('Opening image directory and exiting...')
    log(subreddits, new_download_count, errors)
    time.sleep(1.75)
    os.startfile(target_path)


if __name__ == '__main__':
    # Getting required input from prompts
    subreddit_list = input("Enter subreddit(s) to pull images from separated by commas: ")
    limit = input("Enter number of images to scan from each subreddit: ")

    # Call to get_images with input
    get_images(subreddit_list, limit)






 


    
    

                     
