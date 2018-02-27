#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
from neko2.shared.other import fuzzy, excuses


while True:
    query = input('Query: ')

    partial = fuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzy.best_partial,
        max_results=3,
        min_score=50)

    normal = fuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzy.ratio,
        max_results=3,
        min_score=50)

    quick = fuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzy.quick_ratio,
        max_results=3,
        min_score=50)

    real_quick = fuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzy.real_quick_ratio,
        max_results=3,
        min_score=50)

    deep = fuzzy.extract(
        query,
        excuses.excuses,
        scoring_algorithm=fuzzy.deep_ratio,
        max_results=3,
        min_score=50)

    print('Partial:', partial)
    print('Normal:', normal)
    print('Quick:', quick)
    print('Real Quick:', real_quick)
    print('Deep:', deep)
    print()
