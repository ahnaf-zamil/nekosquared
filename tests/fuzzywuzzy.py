#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
from neko2.shared.other import fuzzywuzzy, excuses


while True:
    query = input('Query: ')

    partial = fuzzywuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzywuzzy.best_partial,
        max_results=3,
        min_score=50)

    normal = fuzzywuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzywuzzy.ratio,
        max_results=3,
        min_score=50)

    quick = fuzzywuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzywuzzy.quick_ratio,
        max_results=3,
        min_score=50)

    real_quick = fuzzywuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzywuzzy.real_quick_ratio,
        max_results=3,
        min_score=50)

    print('Partial:', partial)
    print('Normal:', normal)
    print('Quick:', quick)
    print('Real Quick:', real_quick)
    print()
