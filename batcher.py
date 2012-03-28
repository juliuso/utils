#!/usr/bin/env python
import re, urllib
import os
# Performs a batch download of files in a directory.

url = 'ROOT_URL_OF_DIRECTORY'
links = re.findall('''href=["'](.[^"']+)["']''', urllib.urlopen(url).read(), re.I)

for link in links:
    os.system("curl -OL " + url + '/' + link)
    # or to use wget, uncomment the following line, and uncomment the prior line.
    # os.system("wget " + url + '/' + link)

#cleans filenames, removes %20's and replaces with underscores.

