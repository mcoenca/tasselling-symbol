#!/usr/bin/env python3

import rotten, time, json, traceback, argparse

SLEEP_TIME = 0.3
OUTPUT_DIR = 'rotten'

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

def get_all_rotten(filename, n, out_dir):
    with open(filename, 'r') as f:
        for i, title in enumerate(f):
            if i >= n:
                break
            title = title.strip()
            print('{}/{}: {}'.format(i+1, n, title))
            try:
                info = get_rotten_film_info(title)
                filename = '{}/rotten_{:05}.json'.format(out_dir, i)
                with open(filename, 'w') as out:
                    json.dump(info, out)
                    print('  Wrote data to {}'.format(filename))
            except KeyboardInterrupt:
                break
            except:
                print('  Error')
                traceback.print_exc()                

def main():
    parser = argparse.ArgumentParser(
        description='Fetch film info and reviews from rottentomatoes.com')
    parser.add_argument('films',
        help='File containing film titles, one per line')
    parser.add_argument('numfilms', type=int,
        help='Number of films to fetch from file')
    parser.add_argument('-d', '--dir', default=OUTPUT_DIR,
        help='Directory in which to store fetched data')
    args = parser.parse_args()
    get_all_rotten(args.films, args.numfilms, args.dir)

if __name__ == '__main__':
    main()
