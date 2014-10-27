#!/usr/bin/python3

import metacritic
import json

META_FILM_LIMIT = 10


def get_meta_film_info(title):
    print("Getting listing for {} ... ".format(title), end="")
    results = metacritic.search_movie(1, 2, title)
    searchresults = results['results']
    if len(searchresults) is 0:
        print("Failure: Found no results")
        return None
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
        "title": title,
        "first": first,
        "critic_reviews": critic_reviews,
        "user_reviews": user_reviews
    }
    return everything

def get_all_meta(titles, filename):
    with open(filename,"w") as outfile:
        i = 0
        outfile.write("[")
        for title in titles:
            if i >= META_FILM_LIMIT:
                break
            i += 1
            info = get_meta_film_info(title)
            if info is None:
                print("Failure getting {}".format(title))
            json.dump(info,outfile)
            outfile.write(",")
        outfile.write("]")

def main():
    with open('films', 'r') as f:
        titles = []
        i = 0
        for title in f:
            titles.append(title.strip())
        get_all_meta(titles, "meta_data.json")

if __name__ == '__main__':
    main()
