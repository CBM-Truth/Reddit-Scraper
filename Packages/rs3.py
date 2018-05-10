from auxv2 import compatable, cleanup_title, cleanup_url, size_filter
import urllib.request as web
import urllib
import praw
import os
import os.path
import sys
import time

def get_images(subreddits, max_images, target_path):
        httpErrors = 0
        fileErrors = 0
        encodeErrors = 0

        current_path = os.getcwd()
        reddit = praw.Reddit(
                 client_id='TB0-ZpHZQF6Qog',
                 client_secret='Rz4XNGcDBZVMQE45IpB0EBl-p3s',
                 user_agent='windows:cbm.projects.imagescraper:v2.0 (by /u/PTTruTH)'
                 )

        submissions = []
        downloads = 0

        for sub in subreddits:
            for post in reddit.subreddit(sub).hot(limit=int(max_images)):
                if (compatable(post)):
                    submissions.append(post)

        if (len(submissions) == 0):
            print('No compatable images found.')
            sys.exit()
            
        print(str(len(submissions)) + ' images detected.')
        print('Collecting images...')
        time.sleep(1)

        for post in submissions:
            file_name = cleanup_title(post.title) + '.jpg'
            file = os.path.join(target_path, file_name)
            new_file = os.path.join(current_path, file_name)
            score = post.ups
            if (not os.path.exists(file)): 
                try:
                    imgfile = open(file_name,'wb')
                except FileNotFoundError:
                    print('File not found.')
                    fileErrors += 1 
                    continue
                try:
                    imgfile.write(web.urlopen(cleanup_url(post.url)).read())
                    imgfile.close()
                    os.rename(new_file, file)
                    downloads += 1
                except Exception as e:
                    imgfile.close()
                    os.remove(new_file)
                    fileErrors += 1
                try:
                    print(file_name + ' (Score: ' + str(score) + ') written.')
                except UnicodeEncodeError:
                    print('File written - UnicodeEncodeError.')
                    encodeErrors += 1
            else:
                print('Image already exists.')

        dels = size_filter(target_path)
        print(str(downloads - dels) + ' new image(s) downloaded.')
        print(str(dels) + ' image(s) truncated due to a file size < 300KB.')
        os.startfile(target_path)
        print("File/HTTP Errors: {}, String Encoding Errors: {}"
                .format(str(fileErrors),str(encodeErrors)))
        time.sleep(3)


 


    
    

                     
