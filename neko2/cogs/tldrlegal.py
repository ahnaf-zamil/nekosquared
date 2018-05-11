#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
from typing import Tuple, List

import bs4
from dataclasses import dataclass

# from neko2.shared import traits

base_url = 'https://tldrlegal.com/'


def get_results_from_html(html: str) -> List[Tuple[str, str]]:
    """
    Parses the given HTML as search results for TLDR legal, returning
    a list of tuples for each result: each tuple has the name and URL.
    """
    soup = bs4.BeautifulSoup(html)

    results = soup.find_all(attrs={'class': 'search-result flatbox'})

    pages = []

    for result in results:
        link: bs4.Tag = result.find(name='a')
        url = f'{base_url}{link["href"]}'
        name = link.text
        pages.append((name, url))

    return pages


@dataclass()
class License:
    name: str
    brief: str
    can: List[str]
    cannot: List[str]
    must: List[str]
    full_text: str
    url: str


def get_license_info(html: str) -> License:
    """
    Parses a license info page to get the info regarding said license as an
    object.
    """


if __name__ == '__main__':
    pass