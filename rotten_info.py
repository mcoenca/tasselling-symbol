#!/usr/bin/python3

import rotten, time, json

FILM_LIMIT = 3

def get_rotten_film_info(title):
    time.sleep(0.3)
    response = rotten.search(title)
    if (response['total'] == 0):
        return
    movie = response['movies'][0]
    movie_id = movie['id']
    time.sleep(0.3)
    response = rotten.reviews(movie_id)
    if (response['total'] == 0):
        return
    reviews = response['reviews']
    return {
        "title" : title,
        "movie" : movie,
        "reviews": reviews
    }

def get_all_rotten(titles):
    with open('rotten_info.json', 'w') as out:
        out.write('[')
        for title in titles:
            json.dump(get_rotten_film_info(title), out)
            out.write(',')
        out.write(']')

def main():
    with open('films', 'r') as f:
        titles = []
        i = 0
        for title in f:
            if i >= FILM_LIMIT:
                break
            i += 1
            titles.append(title)
        get_all_rotten(titles)

if __name__ == '__main__':
    main()