#!/usr/bin/env python3

import peewee, traceback, re, math
from rotten_db import *

pattern = re.compile('([?\']|ao$|stars)')

def frac_score(num, denom):
    return min(100, int(100 * num / denom))

def parse_letter_score_modifier(base_score, modifier):
    if modifier in ['+', 'plus']:
        return base_score + 7
    if modifier in ['', '?']:
        return base_score + 4
    if modifier in ['-', 'minus', '--', '=']:
        return base_score
    raise -1

def parse_letter_score(letter, modifier):
    modifier = modifier.strip()
    base_score = 90 - 10 * (ord(letter) - ord('A'))
    return parse_letter_score_modifier(base_score, modifier)

def parse_weird_outof4_4_score(score):
    tokens = score.split('out of')[0].split()
    n = len(tokens)
    if n < 1 or n > 2:
        raise Exception(score)

    if n == 1:
        return frac_score(float(tokens[0]) + 4.4, 8)

    if tokens[0] == 'high':
        return frac_score(float(tokens[1]) + 4.7, 8)
    
    if tokens[0] == 'low':
        return frac_score(float(tokens[1]) + 4, 8)
    
    return Exception(score)

def sanitize_score(score):
    return pattern.sub('', score).strip()

def parse_original_score(score, is_fresh):
    score = sanitize_score(score)

    if not score:
        return -1

    if score[-5:] == 'stars':
        return frac_score(float(score.split()[0]), 5)

    if score[-6:] == '-4..+4':
        return parse_weird_outof4_4_score(score)

    tokens = score.split('/')
    n_tok = len(tokens)
    if n_tok > 2 or n_tok < 1:
        raise Exception(score)
    if n_tok == 2:
        return frac_score(float(tokens[0]), float(tokens[1]))

    tokens = score.split('out of')
    n_tok = len(tokens)
    if n_tok > 2 or n_tok < 1:
        raise Exception(score)
    if n_tok == 2:
        return frac_score(float(tokens[0]), float(tokens[1]))

    tokens = score.split('of')
    n_tok = len(tokens)
    if n_tok > 2 or n_tok < 1:
        raise Exception(score)
    if n_tok == 2:
        return frac_score(float(tokens[0]), float(tokens[1]))

    c = score[:1].upper()
    if 'A' <= c and c <= 'F':
        return parse_letter_score(c, score[1:])

    x = float(score)
    if x <= 5 and is_fresh:
        return frac_score(x, 5)
    if x <= 10:
        return frac_score(x, 10)
    if x <= 20:
        return frac_score(x, 20)

    raise Exception(score)

def process_scores():
    query = Review.select(
        Review.id,
        Review.original_score,
        Review.is_fresh)

    for review in query:
        if not review.original_score:
            continue

        try:
            score = parse_original_score(
                review.original_score,
                review.is_fresh)
            #if score == 0:
            #    print("Zero score {}".format(review.original_score))
        except Exception:
            #traceback.print_exc()
            print("Could not parse score {}".format(review.original_score))
            if review.is_fresh:
                score = 75
            else:
                score = 25

        review.score = score
        review.save()

def remove_duplicate_reviews():
    top_reviews = (Review
        .select(
            Review.id, 
            Movie.id,
            Movie.title,
            Critic.id,
            Critic.name,
            Review.date)
        .join(Movie)
        .switch(Review)
        .join(Critic)
        .where(Review.is_top == True)
        .order_by(Review.critic))

    already_dedup = set()

    for review in top_reviews:
        tup = (review.critic.id, review.movie.id, review.date)
        if tup in already_dedup:
            print('Already deduped', tup)
            continue
        already_dedup.add(tup)
        delete_dup_reviews = (review
            .delete()
            .where((Review.is_top == True) & 
                (Review.critic == review.critic) &
                (Review.movie == review.movie) &
                (Review.id != review.id) &
                (Review.date == review.date)))
        delete_dup_reviews.execute()

def main():
    with db.transaction():
        #remove_duplicate_reviews()
        process_scores()

if __name__ == '__main__':
    main()
