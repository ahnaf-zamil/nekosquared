#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Various package management utilities.
"""
import aiohttp
from discomaton import book
from neko2.shared import commands, traits


async def search_aur(sesh: aiohttp.ClientSession, criteria: str):
    # https://wiki.archlinux.org/index.php/AurJson
    async with sesh.get(
        "https://aur.archlinux.org/rpc/",
        params={"v": 5, "type": "search", "arg": criteria},
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()

    return data


async def info_aur(sesh: aiohttp.ClientSession, package: str):
    # https://wiki.archlinux.org/index.php/AurJson
    async with sesh.get(
        "https://aur.archlinux.org/rpc/",
        params={"v": 5, "type": "info", "arg": package},
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
    return data
