#!/usr/bin/python3

import rotten, time, json

FILM_LIMIT = 3

def get_rotten_film_info(title):
    time.sleep(0.3)
    ans = { "title" : title }
    
    response = rotten.search(title)
    if (response['total'] == 0):
        return ans

    movie = response['movies'][0]
    ans['movie'] = movie

    movie_id = movie['id']
    time.sleep(0.3)
    response = rotten.reviews(movie_id)
    if (response['total'] == 0):
        return ans

    reviews = response['reviews']
    ans['reviews'] = reviews
    return ans

def get_all_rotten(titles):
    with open('rotten_info.json', 'w') as out:
        out.write('[')
        n = len(titles)
        for i, title in enumerate(titles):
            print('{}/{}: {}'.format(i+1, n, title))
            try:
                info = get_rotten_film_info(title)
                json.dump(info, out)
            except:
                print('Error')
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
            titles.append(title.strip())
        get_all_rotten(titles)

if __name__ == '__main__':
    main()