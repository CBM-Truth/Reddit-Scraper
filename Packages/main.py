import urllib.request as web
import ctypes as c 
import urllib, praw, os, os.path, sys, time
    
user = c.windll.user32

SCREEN_WIDTH = user.GetSystemMetrics(0) 
SCREEN_HEIGHT = user.GetSystemMetrics(1)

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
    if not os.path.exists('log.txt'):
        mode = 'w'
    else:
        mode = 'a'
    f = open('log.txt', mode)
    reddits = reddits.replace(' ', '')
    reddits = reddits.replace(',', ', ')
    current_time = time.asctime(time.localtime(time.time()))
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
    delimiters = ['[',']','(',')']
    width, height = '', ''
    res = []
    for char in delimiters:
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
def compatable(post):
    width, height = get_resolution(post.title)
    return width >= SCREEN_WIDTH and height >= SCREEN_HEIGHT and width > height

#post: removes problematic characters from a reddit post title for parsing,
# returns a new cleaned up string
def cleanup_title(text):
    chars = ['/','\\',':','*','?','<','>','"','|']
    for char in chars:
        if char in text:
            text = text.replace(char, '')
    return text

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

#pre: subreddits is an array of subreddit strings without spaces, throws an exception otherwise
#pre: target_path is a valid directory, throws and exception if otherwise
#post: downloads all compatable images from the passed subreddits, searches for a max of max_images from
#each subreddit. All images are placed in the target_path destination at the end of runtime
def get_images(subreddits, _max, target_path):
        httpErrors = 0
        fileErrors = 0
        encodeErrors = 0
        current_path = os.getcwd()
        reddit = praw.Reddit(
                 client_id='TB0-ZpHZQF6Qog',
                 client_secret='Rz4XNGcDBZVMQE45IpB0EBl-p3s',
                 user_agent='windows:cbm.projects.imagescraper:v2.0 (by /u/PTTruTH)'
                 )
        good_posts = []
        downloads = 0
        print('Detected Resolution: [{}x{}]'.format(str(SCREEN_WIDTH), str(SCREEN_HEIGHT)))

        for sub in subreddits.replace(' ', '').split(','):
            if 'porn' not in sub:
                sub += 'porn'
            for post in reddit.subreddit(sub).hot(limit=int(_max)):
                if compatable(post):
                    good_posts.append(post)

        if len(good_posts) == 0:
            print('No compatable images found') 
            sys.exit()
            
        print(str(len(good_posts)) + ' images detected')
        print('Collecting images...')
        time.sleep(1)

        for post in good_posts:
            file_name = cleanup_title(post.title) + '.jpg'
            stored_file = os.path.join(target_path, file_name)
            raw_file = os.path.join(current_path, file_name)
            if not os.path.exists(stored_file): 
                try:
                    _file = open(file_name,'wb')
                except FileNotFoundError as e:
                    print('File not found')
                    fileErrors += 1 
                    continue
                try:
                    _file.write(web.urlopen(cleanup_url(post.url)).read())
                    _file.close()
                    os.rename(raw_file, stored_file)
                    downloads += 1
                except Exception:
                    print('Unable to write file')
                    _file.close()
                    os.remove(raw_file)
                    fileErrors += 1
                print(file_name.encode('ascii', 'ignore').decode() + ' (' + str(post.ups) + ' upvotes) written') 
            else:
                print('Image already exists')

        dels = size_filter(target_path)
        new_download_count = downloads - dels
        print(str(new_download_count) + ' new image(s) downloaded')
        print(str(dels) + ' image(s) truncated due to a file size < 300KB')
        errors = 'File/HTTP Errors: {}, String Encoding Errors: {}'.format(str(fileErrors),str(encodeErrors))
        print(errors)
        print('Opening image directory and exiting...')
        log(subreddits, new_download_count, errors)
        time.sleep(1.5)
        os.startfile(target_path)

#####################################################
#Main----->

#Getting required input from prompts
subs = input("Enter subreddit(s) to pull images from spereated by commas: ")
_max = input("Enter max number of images to consider from each subreddit: ")
        
#Call to get_images with required input
get_images(subs, _max, get_target_path())






 


    
    

                     
