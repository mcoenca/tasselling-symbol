#!/usr/bin/python3

import rotten

FILM_LIMIT = 10

def get_rotten_film_info(title):
    results = rotten.search(title)
    print(results)
    return None

def main():
    with open('films', 'r') as f:
        i = 0
        for title in f:
            if i >= FILM_LIMIT:
                break
            i += 1
            info = get_rotten_film_info(title)

if __name__ == '__main__':
    main()