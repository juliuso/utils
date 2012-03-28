#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import string
import urllib2
from xml.dom.minidom import parse
import random
import re
"""
README

- Developed in Python v2.7.1 on OS X.
- All modules from Python Standard Library. No external dependencies.
- Cannot ensure full unicode support.
- Best effort made to suppress errors, and prevent interruption.
- Did not have time to implement MD5 hashing to cache data for fast lookups.
- Queries converted to lowercase before processing.
- Used arbitrary interval to slice poem into substrings. Using a
  lexical analysis library as nltk might do a better job, but unfamiliar
  with implementation.
- Example poem from programming assignment resolves successfully.
- Multithreaded downloads implemented. Processing starts after completion.

Julius O
25-Mar-2012

"""
# BEGIN: Define global constants.
BASE_SEARCH_URL = "http://ws.spotify.com/search/1/track?q="

BASE_TRACK_URL  = "http://open.spotify.com/track/"

USER_PROMPT = ("\nEnter poem and press <Enter> to generate playlist.\n\
Press 's' and <Enter> to generate the example playlist.\n\
Press 'x' and <Enter> to quit: \n\n")

WAITING_MESSAGE = ("Talking to Spotify.\n\
Processing times dependent on poem length.\n\
One moment please...\n")

ENTER_TO_CONTINUE = "\nPress <Enter> to continue."

WORD_LENGTH_MINIMUM = 3

ERROR_WORD_MINIMUM = 7

RANDOM_SAMPLE_MINIMUM = 4

ERROR_WORD_MINIMUM_MSG = ("Please enter at least seven(7) words.\
Then press <Enter>.")
# END: Define global constants.

# Stores multithreading download threads.
threads = []

# Cached poem dictionary. Not yet implemented.
track_hash = {}

# Stores input of user's poem.
poem_input = []

# After user's poem is processed, the poem is reset to the default poem.
default_poem = ['If I Can\'t', 'Let It Go', 'Out Of My Mind',
                'I\'m Scared', 'My Stupid Heart', 'My Stupid Mouth',
                'Will Try', 'Finding a Way Home', 'Home To You',
                'Letting You Know', 'All The Ways',
                'I Want The World To Stop', 'With You']

# Example poem from the programming exercise.
# This is overwritten when a user's poem is processed.
poem = ['If I Can\'t', 'Let It Go', 'Out Of My Mind',
        'I\'m Scared', 'My Stupid Heart', 'My Stupid Mouth',
        'Will Try', 'Finding a Way Home', 'Home To You',
        'Letting You Know', 'All The Ways',
        'I Want The World To Stop', 'With You']

# Stores XML document objects from the download.
poem_objects = [None] * len(poem)

# Returns each poem object to lowercase.
def getString(i):
    return poem[i].lower()

# Cleans up the query string before connecting to API.
def encodeString(i):
    condition = re.sub(' ','+', getString(i))
    return condition

# Returns an XML document object from the API.
def getStringXML(i):
    xml_query = parse(urllib2.urlopen(\
                      BASE_SEARCH_URL + encodeString(i)))
    track_check = xml_query.getElementsByTagName('track')

    # Checks for the existence of track tags to process.
    if len(track_check) > 0:
        return xml_query
    else:
        return getRandomStringXML()

# When no valid XML object is returned, sample population and try again.
# Must behave exactly like getStringXML(), returning a parsed XML object.
def getRandomStringXML():
    random.seed()
    population = []
    word_sample = []

    for p in poem:
        if len(p) > WORD_LENGTH_MINIMUM:
            population.append(p)

    word_sample = random.sample(population, RANDOM_SAMPLE_MINIMUM)
    joined_word_sample = string.join(RANDOM_SAMPLE_MINIMUM).lower()
    encoded_word_sample = re.sub(' ','+', joined_word_sample)
    xml_query = parse(urllib2.urlopen(\
                      BASE_SEARCH_URL + encoded_word_sample))

    track_check = xml_query.getElementsByTagName('track')

    if len(track_check) > 0:
        return xml_query
    else:
        getRandomStringXML()

# Helper function for parseStringXML().
def getPoemObject(i):
    return poem_objects[i]

# Parses an XML object for elements and attributes, returning a list object.
def parseStringXML(i):
    results = []

    try:
        tracks  = getPoemObject(i).getElementsByTagName('track')

        for track in tracks:
            track_id = track.getAttribute('href')
            track_names = track.getElementsByTagName('name')
            track_name_count = 0
            for track_name in track_names:
                if track_name_count < 1:
                    name = track_name.childNodes[0].nodeValue
                    results.append(track_id[14:])
                    results.append(name.lower())
                    track_name_count += 1
                else:
                    break
    except AttributeError, UnboundLocalError:
        pass

    return results

# Processes an XML list object, and attempts to match string.
def matchStringToXML(i):
    track_names = parseStringXML(i)
    poem_string = getString(i)

    if poem_string in track_names:
        # "Match Condition 1: Exact match in list item."
        return track_names[track_names.index(poem_string)-1]
    elif poem_string not in track_names:
        for track_name in track_names:
            if poem_string in track_name:
                # "Match Condition 2: Substring match found in list item."
                return track_names[track_names.index(track_name)-1]
        else:
            # "Match Condition 3: No match. Random sample from population."
            return getRandomTrack(i)

# In the event of no match, a random match is made from available data.
def getRandomTrack(i):
    random.seed()
    track_ids = []
    track_names = parseStringXML(i)
    selection = []

    try:
        for track in track_names:
            track_index = track_names.index(track)
            if track_index % 2 == 0 or track_index == 0:
                track_ids.append(track)

        selection = random.sample(track_ids, 1)
    except ValueError:
        pass

    try:
        return selection[0]
    except IndexError:
        pass

# Create Spotify track URL for each object.
def createStringToURL(i):
    try:
        print BASE_TRACK_URL + matchStringToXML(i)
    except TypeError:
        pass
    return 0

# Processes poem from user input.
# At this point, poem_input has been split into individual words.
def processPoemInput():
    global poem_input
    global poem
    global poem_objects
    poem = []
    poem_slice = []

    for i in range(len(poem_input)):
        try:
            poem_slice.append(poem_input[i:i+4])
        except IndexError:
            continue

    for fragment in poem_slice:
        poem.append(' '.join(fragment))

    poem_objects = [None] * len(poem)
    return poem

# After poem from user input is processed, reset poem to the example poem.
def resetPoem():
    global poem
    poem = default_poem
    return 0

# BEGIN: Implement multithreaded downloads.
def worker():
    try:
        for i in range(len(poem)):
            poem_objects[i] = getStringXML(i)
    except TypeError:
        pass
    return 0

def startWorker():
    for i in range(9):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    return 0

def waitForWorkerToFinish():
    for t in threads:
        t.join()
    return 0
# END: Implement multithreaded downloads.

# BEGIN: Implement main function.
def start():
    global poem_input
    prompt = raw_input(USER_PROMPT)
    string_prompt = prompt.strip()

    # Processes the example poem.
    if string_prompt == 's' or string_prompt == 'S':
        print WAITING_MESSAGE
        startWorker()
        waitForWorkerToFinish()

        for i in range(len(poem)):
            createStringToURL(i)

        raw_input(ENTER_TO_CONTINUE)
        start()
    # Quits the program.
    elif string_prompt == 'x' or string_prompt == 'X':
        exit()
    # If the poem is too short, prompts user to re-enter.
    elif len(string_prompt.split()) < ERROR_WORD_MINIMUM:
        print ERROR_WORD_MINIMUM_MSG
        raw_input(ENTER_TO_CONTINUE)
        start()
    # Processes the user's poem input.
    else:
        print WAITING_MESSAGE
        poem_input = string_prompt.split()
        processPoemInput()
        startWorker()
        waitForWorkerToFinish()

        for i in range(len(poem)):
            createStringToURL(i)

        raw_input(ENTER_TO_CONTINUE)
        resetPoem()
        start()
    return 0
# END: Implement main function.

# Start the program.
start()