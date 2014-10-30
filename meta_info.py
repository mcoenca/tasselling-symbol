#!/usr/bin/env python3

import metacritic
import json
import traceback

META_FILM_LIMIT = 5000


def get_meta_film_info(title, key):
    print("Getting listing for {} ... ".format(title), end="")
    results = metacritic.search_movie(1, 2, title)
    if 'results' not in results:
        everything = {
            "key": key,
            "title": title,
            "first": None,
            "critic_reviews": None,
            "user_reviews": None
        }
        return everything
    searchresults = results['results']
    if len(searchresults) is 0:
        everything = {
            "key": key,
            "title": title,
            "first": None,
            "critic_reviews": None,
            "user_reviews": None
        }
        return everything
    print("Success")
    first = searchresults[0]
    url = first['url']
    print("Getting critic reviews for {} ... ".format(title), end="")
    critic_reviews = metacritic.critic_reviews(url)
    if 'count' in critic_reviews:
        print("Successfully got {} reviews".format(critic_reviews['count']))
    else:
        print("Failure")
    print("Getting user reviews for {} ... ".format(title), end="")
    user_reviews = metacritic.user_reviews(url,'all')
    if 'count' in user_reviews:
        print("Successfully got {} reviews".format(user_reviews['count']))
    else:
        print("Failure")
    everything = {
        "key": key,
        "title": title,
        "first": first,
        "critic_reviews": critic_reviews,
        "user_reviews": user_reviews
    }
    return everything


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
        


def get_all_meta(titles, filename, start, end):
    i = start
    while True:
        title = titles[i]
        if i >= end:
            break
        this_filename = str(filename)+"_"+str(i)+".json"
        write_file(title,this_filename,i,start,end)
        i += 1


def main():
    with open('films', 'r') as f:
        titles = []
        for title in f:
            titles.append(title.strip())
        get_all_meta(titles, "meta2/meta", 2400, META_FILM_LIMIT)

if __name__ == '__main__':
    main()
