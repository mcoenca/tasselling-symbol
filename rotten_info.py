#!/usr/bin/env python3

import rotten, time, json, traceback

SLEEP_TIME = 0.3
FILM_LIMIT = 3

def get_all_reviews(movie_id, review_type):
    ans = []
    time.sleep(SLEEP_TIME)
    response = rotten.reviews(movie_id, review_type=review_type)
    if (response['total'] == 0):
        return ans
    reviews = response['reviews']
    ans = reviews
    
    next = response['links'].get('next', None)
    while next:
        time.sleep(SLEEP_TIME)
        response = rotten.get(next)
        if (response['total'] == 0):
            return ans
        ans.extend(response['reviews'])
        next = response['links'].get('next', None)

    return ans

def get_rotten_film_info(title):
    time.sleep(SLEEP_TIME)
    ans = { "title" : title }
    
    response = rotten.search(title)
    if (response['total'] == 0):
        return ans
    movie = response['movies'][0]
    ans['movie'] = movie
    print('  Got movie info')

    movie_id = movie['id']

    reviews_top = get_all_reviews(movie_id, 'top_critic')
    print('  Got top reviews: {}'.format(len(reviews_top)))
   
    reviews_all = get_all_reviews(movie_id, 'all') 
    print('  Got all reviews: {}'.format(len(reviews_all)))

    ans['reviews'] = {
        'top_critic': reviews_top, 
        'all' : reviews_all
    }

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
                print('  Error')
                traceback.print_exc()                
            if i < n-1:
                out.write(',')
        out.write(']')

def main():
    with open('films', 'r') as f:
        titles = []
        for i,title in enumerate(f):
            if i >= FILM_LIMIT:
                break
            titles.append(title.strip())
        get_all_rotten(titles)

if __name__ == '__main__':
    main()
