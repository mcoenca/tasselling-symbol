#!/usr/bin/python3

import metacritic
import json

META_FILM_LIMIT = 10


def get_meta_film_info(title):
    results = metacritic.search_movie(1, 2, title)
    print(results)
    searchresults = results['results']
    if len(searchresults) is 0:
        return None
    first = searchresults[0]
    url = first['url']
    critic_reviews = metacritic.critic_reviews(url)
    user_reviews = metacritic.user_reviews(url, 100)
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
            json.dump(info,outfile)
            outfile.write(",")
        outfile.write("]")

def main():
    with open('films', 'r') as f:
        titles = []
        i = 0
        for title in f:
            if i >= FILM_LIMIT:
                break
            i += 1
            titles.append(title)
        get_all_meta(titles)

if __name__ == '__main__':
    main()
