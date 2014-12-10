#!/usr/bin/env python3

import peewee, traceback, re, math
import rotten_db as db

pattern = re.compile('([?\']|ao$|stars)')

def frac_score(num, denom):
    return min(100, int(100 * num / denom))

def parse_letter_score_modifier(base_score, modifier):
    if modifier in ['+', 'plus']:
        return base_score + 15
    if modifier in ['', '?']:
        return base_score + 7
    if modifier in ['-', 'minus', '--', '=']:
        return base_score
    return None

def parse_letter_score(letter, modifier):
    modifier = modifier.strip()
    base_score = 80 - 20 * (ord(letter) - ord('A'))
    if letter == 'F':
        base_score += 20
    return parse_letter_score_modifier(base_score, modifier)

def parse_weird_outof4_4_score(score):
    tokens = score.split('out of')[0].split()
    n = len(tokens)
    if n < 1 or n > 2:
        return None

    if n == 1:
        return frac_score(float(tokens[0]) + 4.4, 8)

    if tokens[0] == 'high':
        return frac_score(float(tokens[1]) + 4.7, 8)
    
    if tokens[0] == 'low':
        return frac_score(float(tokens[1]) + 4, 8)
    
    return None

def sanitize_score(score):
    return pattern.sub('', score).strip()

def parse_original_score_exc(score, is_fresh):
    if not score:
        return None

    score = sanitize_score(score)

    if not score:
        return None

    if score[-5:] == 'stars':
        return frac_score(float(score.split()[0]), 5)

    if score[-6:] == '-4..+4':
        return parse_weird_outof4_4_score(score)

    tokens = score.split('/')
    n_tok = len(tokens)
    if n_tok > 2 or n_tok < 1:
        return None
    if n_tok == 2:
        return frac_score(float(tokens[0]), float(tokens[1]))

    tokens = score.split('out of')
    n_tok = len(tokens)
    if n_tok > 2 or n_tok < 1:
        return None
    if n_tok == 2:
        return frac_score(float(tokens[0]), float(tokens[1]))

    tokens = score.split('of')
    n_tok = len(tokens)
    if n_tok > 2 or n_tok < 1:
        return None
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

    return None

def parse_original_score(original_score, is_fresh):
    try:
        score = parse_original_score_exc(original_score, is_fresh)
    except Exception:
        score = None

    if score == None:
        if original_score != None:
            print(" could not parse score")
        if is_fresh:
            score = 75
        else:
            score = 25

    return score

def process_scores():
    query = (db.Review
        .select(
            db.Review.id,
            db.Review.original_score,
            db.Review.is_fresh))

    for i, review in enumerate(query):
        print("\rProcessing review {}: {} ..."
                .format(i, review.original_score), end='')

        review.score = parse_original_score(
                review.original_score,
                review.is_fresh)

        review.save()

def remove_duplicate_reviews():
    top_reviews = (db.Review
        .select(
            db.Review.id, 
            Movie.id,
            Movie.title,
            Critic.id,
            Critic.name,
            db.Review.date)
        .join(Movie)
        .switch(db.Review)
        .join(Critic)
        .where(db.Review.is_top == True)
        .order_by(db.Review.critic))

    already_dedup = set()

    for review in top_reviews:
        tup = (review.critic.id, review.movie.id, review.date)
        if tup in already_dedup:
            print('Already deduped', tup)
            continue
        already_dedup.add(tup)
        delete_dup_reviews = (review
            .delete()
            .where((db.Review.is_top == True) & 
                (db.Review.critic == review.critic) &
                (db.Review.movie == review.movie) &
                (db.Review.id != review.id) &
                (db.Review.date == review.date)))
        delete_dup_reviews.execute()

def main():
    with db.db.transaction():
    #    remove_duplicate_reviews()
        process_scores()

if __name__ == '__main__':
    main()
