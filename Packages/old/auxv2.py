import os
import os.path

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_resolution(title):
    delimiters = ['[',']','(',')']
    width, height = '', ''
    res = []
    for char in delimiters:
        if char in title:
            title = title.replace(char, '')
    title = list(title)
    for i in range(len(title)):
        if (is_float(title[i]) and i >= len(title)*0.6):
            res.append(title[i])
    for element in res[:int(len(res) / 2)]:
        width += element
    for element in res[int(len(res) / 2):]:
        height += element
    if (len(width) == 0 or len(height) == 0):
            width, height = 0, 0
    return int(width), int(height)

def compatable(post):
    width,height = get_resolution(post.title)
    return (width >= 1920 and height >= 1080) and (width > height)

def cleanup_title(text):
    chars = ['/','\\',':','*','?','<','>','"','|']
    for char in chars:
        if char in text:
            text = text.replace(char, '')
    return text
 
def cleanup_url(url):
    retStr = url
    url = url.split('.')
    if (url[len(url) - 1] != 'jpg'):
            retStr += '.jpg'
    return retStr

def size_filter(main_path):
    dels = 0
    for sub_path in os.listdir(main_path):
        file = os.path.join(main_path, sub_path)
        if (os.path.getsize(file) / 1000 < 300):
            os.remove(file)
            dels += 1
    return dels
    
