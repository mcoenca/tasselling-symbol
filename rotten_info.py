#!/usr/bin/env python3

import rotten, time, json, traceback, argparse, os.path

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

def complete_film_info(info, title):
    changed = False
    time.sleep(SLEEP_TIME)
    info['title'] = title
    
    if 'movie' in info:
        print('  Already had movie info')
        movie = info['movie']
    else:
        response = rotten.search(title)
        if (response['total'] == 0):
            return changed
        movie = response['movies'][0]
        info['movie'] = movie
        changed = True
        print('  Fetched movie info')

    movie_id = movie['id']

    if 'top_critic_reviews' in info:
        print('  Already had top critic reviews')
    else:
        reviews_top = get_all_reviews(movie_id, 'top_critic')
        print('  Fetched top critic reviews: {}'.format(len(reviews_top)))
        info['top_critic_reviews'] = reviews_top
        changed = True
   
    if 'all_reviews' in info:
        print('  Already had all reviews')
    else:
        reviews_all = get_all_reviews(movie_id, 'all') 
        print('  Fetched all reviews: {}'.format(len(reviews_all)))
        info['all_reviews'] = reviews_all
        changed = True

    return changed

def get_one_film(title, filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            info = json.load(f)
    else:
        info = dict()

    changed = complete_film_info(info, title)

    if changed:
        with open(filename, 'w') as out:
            json.dump(info, out)
            print('  Wrote data to {}'.format(filename))
    else:
        print('  Nothing changed, no need to overwrite')


def get_all_rotten(filename, n, out_dir):
    with open(filename, 'r') as f:
        for i, title in enumerate(f):
            if i >= n:
                break
            title = title.strip()
            print('{}/{}: {}'.format(i+1, n, title))
            try:
                filename = '{}/rotten_{:05}.json'.format(out_dir, i)
                get_one_film(title, filename)
            except KeyboardInterrupt:
                break
            except:
                print('  Error')
                traceback.print_exc()
            if i < n-1:
                print()

def main():
    parser = argparse.ArgumentParser(
        description='Fetch film info and reviews from rottentomatoes.com')
    parser.add_argument('films',
        help='File containing film titles, one per line')
    parser.add_argument('numfilms', type=int,
        help='Number of films to fetch from file')
    parser.add_argument('-d', '--dir', default=OUTPUT_DIR,
        help='Directory in which to store fetched data (default: {})'.
        format(OUTPUT_DIR))
    args = parser.parse_args()
    get_all_rotten(args.films, args.numfilms, args.dir)

if __name__ == '__main__':
    main()
