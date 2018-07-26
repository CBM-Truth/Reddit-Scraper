import urllib.request as web
import ctypes as c 
import urllib, praw, os, os.path, sys, time
    
user = c.windll.user32

SCREEN_WIDTH = user.GetSystemMetrics(0) 
SCREEN_HEIGHT = user.GetSystemMetrics(1)
CURRENT_PATH = os.getcwd()
MAX_FILENAME_LENGTH = 170

#post: If there is no file present containg a target location, a new file is made
# and the path is written. Will read the path from the file and return it as a string
def get_target_path():
    path = ''
    if not os.path.exists('target_path.txt'):
        target_path_input = input('Please enter a destination folder: ')
        create_target_path(target_path_input)
    with open('target_path.txt') as f:
        path = f.read()
        f.close()
    return path

#post: Writes the path argument to a new text file named 'target_path.txt'
def create_target_path(path):
    f = open('target_path.txt', 'w')
    f.write(path)
    f.close()

#post: logs time of current execution to a log file on startup
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

#post: Returns true if argument is of the float class, false otherwise
def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#post: Returns the resolution embedded in a reddit post title in (width, height) form
def get_resolution(title):
    delims = ['[',']','(',')']
    width, height = '', ''
    res = []
    for char in delims:
        if char in title:
            title = title.replace(char, '')
    title = list(title)
    for i in range(len(title)):
        if is_float(title[i]) and i >= len(title)*0.6:
            res.append(title[i])
    mid = int(len(res) / 2)
    for element in res[:mid]:
        width += element
    for element in res[mid:]:
        height += element
    if len(width) == 0 or len(height) == 0:
            width, height = 0, 0
    return int(width), int(height)


#post: Returns true if the resolution in the post title is at least 1920x1080 and if width > height
#returns false otherwise
def compatable(path, post):
    width, height = get_resolution(post.title)
    flickr_image = 'https://www.flickr.com/' in post.url
    on_disk = os.path.exists(os.path.join(path, cleanup_title(post.title)))
    correct_dimensions = width >= SCREEN_WIDTH and height >= SCREEN_HEIGHT and width > height
    return not flickr_image and not on_disk and correct_dimensions

#post: removes problematic characters from a reddit post title for parsing,
# returns a new cleaned up string
def cleanup_title(text):
    chars = ['/','\\',':','*','?','<','>','"','|']
    for char in chars:
        if char in text:
            text = text.replace(char, '')
    return text + '.jpg'

#post: appends .jpg the image url if it isn't already present, returns a new string 
def cleanup_url(url):
    retStr = url
    url = url.split('.')
    if url[len(url) - 1] != 'jpg':
            retStr += '.jpg'
    return retStr

#post: removes files < 300KB from the argument path. Returns the number of files removed
# as an integer
def size_filter(main_path):
    dels = 0
    for sub_path in os.listdir(main_path):
        _file = os.path.join(main_path, sub_path)
        if os.path.getsize(_file) / 1000 < 300:
            os.remove(_file)
            dels += 1
    return dels

#pre: subreddits is an array of subreddit strings, throws an exception otherwise
#pre: target_path is a valid directory, throws and exception if otherwise
#post: downloads all compatable images from the passed subreddits, searches for a max of max_images from
#each subreddit. All images are placed in the target_path destination at the end of runtime
def get_images(subreddits, _max, target_path):
        errors = 0
        downloads = 0
        compatable_posts = []
        reddit = praw.Reddit(
                 client_id='TB0-ZpHZQF6Qog',
                 client_secret='Rz4XNGcDBZVMQE45IpB0EBl-p3s',
                 user_agent='windows:cbm.projects.imagescraper:v2.0 (by /u/PTTruTH)'
                 )
        print('Detected Resolution: [{}x{}]'.format(str(SCREEN_WIDTH), str(SCREEN_HEIGHT)))

        for sub in subreddits.replace(' ', '').split(','):
            if 'porn' not in sub:
                sub += 'porn'
            for post in reddit.subreddit(sub).hot(limit=int(_max)):
                if compatable(target_path, post):
                    compatable_posts.append(post)

        if len(compatable_posts) == 0:
            print('No compatable images found') 
            sys.exit()
            
        print(str(len(compatable_posts)) + ' compatable images detected')
        print('Collecting images...\n')
        time.sleep(1)

        for post in compatable_posts:
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
            except Exception:
                print('Unable to write file: ' + filename + ' (' + post.url + ')')
                _file.close()
                os.remove(raw_file)
                errors += 1
            print(filename.encode('ascii', 'ignore').decode() + ' (' + str(post.ups) + ' upvote(s)) written') 

        dels = size_filter(target_path)
        new_download_count = downloads - dels
        print('\n' + str(new_download_count) + ' new image(s) downloaded')
        if dels > 0: print(str(dels) + ' image(s) smaller than 300KB removed')
        errors = 'HTTP Errors: {}'.format(str(errors))
        print(errors)
        print('Opening image directory and exiting...')
        log(subreddits, new_download_count, errors)
        time.sleep(1.75)
        os.startfile(target_path)

#Main--

#Getting required input from prompts
subs = input("Enter subreddit(s) to pull images from spereated by commas: ")
_max = input("Enter number of images to scan from each subreddit: ")
        
#Call to get_images with input
get_images(subs, _max, get_target_path())






 


    
    

                     
