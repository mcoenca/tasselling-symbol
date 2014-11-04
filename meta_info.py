#!/usr/bin/env python3

import meta
import json
import traceback
import argparse
import os
from os.path import isfile, join
import errno

META_FILM_LIMIT = 4999
FILE_FORMAT = '{}/meta-{}.json'


def valid_film(film):
    if not film:
        return False
    if 'name' in film:
        return True
    return False


def get_film(title):
    print("Getting listing for {} ... ".format(title), end="")
    exact = meta.find_movie(4,title)
    if valid_film(exact):
        print("Success")
        return exact
    search = meta.search_movie(1, 4, title)
    if not search or 'results' not in search:
        print("Failure")
        return None
    results = search['results']
    if len(results) is 0:
        print("Failure")
        return None
    print("Success")
    return results[0]

def get_critic_reviews(url, title):
    print("Getting critic reviews for {} ... ".format(title), end="")
    critic_reviews = meta.critic_reviews(url)
    if critic_reviews and 'count' in critic_reviews:
        print("Successfully got {} reviews".format(critic_reviews['count']))
        return critic_reviews
    else:
        print("Failure")
        return None

def get_user_reviews(url, title):
    print("Getting user reviews for {} ... ".format(title), end="")
    user_reviews = meta.user_reviews(url,'all')
    if user_reviews and 'count' in user_reviews:
        print("Successfully got {} reviews".format(user_reviews['count']))
        return user_reviews
    else:
        print("Failure")
        return None

def write_file(title, filename, i, start, end):
    with open(filename,"w") as outfile:
        print("{} : {}/{} -- ".format(i, i-start, end-start),end="")
        try:
            info = get_meta_film_info(title, i)
            if info is None:
                print("Failure getting {}".format(title))
            else:
                json.dump(info,outfile)
        except:
            print("Error")
            traceback.print_exc()

def init_file(name, key, filename):
    with open(filename,"w") as outfile:
        temp = {
            "key" : key,
            "title" : name,
            "film" : None,
            "critic_reviews" : None,
            "user_reviews" : None,
        }
        json.dump(temp, outfile)

def init_all(filename, dirname, limit):
    try:
        os.makedirs(dirname)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    with open(filename, 'r') as f:
        titles = []
        for i,t in enumerate(f):
            title = t.strip()
            filename = FILE_FORMAT.format(dirname, i)
            init_file(title, i, filename)
            if(i >= limit - 1):
                break

        
def fill_file(filename):
    json_data = None
    with open(filename,'r') as data:
        try:
            json_data = json.load(data)
        except:
            print("failed to load json data")
            traceback.print_exc()
            return
   
    title = json_data['title']
    film = json_data['film']
    critic_reviews = json_data['critic_reviews']
    user_reviews = json_data['user_reviews']

    if title and film and critic_reviews and user_reviews:
        return
    if not valid_film(film):
        film = get_film(title)
    if not valid_film(film):
        return

    json_data['film'] = film
    url = film['url']
    if not critic_reviews:
        critic_reviews = get_critic_reviews(url, title)
        json_data['critic_reviews'] = critic_reviews
    if not user_reviews:
        user_reviews = get_user_reviews(url, title)
        json_data['user_reviews'] = user_reviews

    with open(filename, "w") as outfile:  
        json.dump(json_data, outfile)

def fill_all(dirname):
    onlyfiles = [ f for f in os.listdir(dirname) if isfile(join(dirname,f)) ]
    for filename in onlyfiles:
        fill_file(str(join(dirname,filename)))

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-d','--dir', dest='dir', metavar='f', 
            help='an integer for the accumulator',required=True)
    parser.add_argument('-i','--init', dest='init', metavar='d',
            help='sum the integers (default: find the max)')
    args = vars(parser.parse_args())
    dirname = args['dir']
    if args['init']:
        init_all(args['init'], dirname, META_FILM_LIMIT)
    else:
        fill_all(dirname)

if __name__ == '__main__':
    main()
