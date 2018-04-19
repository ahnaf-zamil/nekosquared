#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Compiler/interpreter for CRAN-R.

Reverse engineered from the online https://rdrr.io CRAN-R interpreter.
"""
import asyncio
import base64
import json
from typing import Optional, List, Tuple

import aiohttp
import async_timeout
from dataclasses import dataclass

HOST = 'https://rdrr.io'

INVOKE_EP = '/snippets/run'
INVOKE_REQ = 'POST'

RETRIEVE_EP = '/snippets/get/'
RETRIEVE_REQ = 'GET'


@dataclass()
class CranRResult:
    fail_reason: Optional[str]
    state: str
    result: str
    images: List[Tuple[bytes, str]]  # Bytes against string type.
    output: str


async def eval_r(source: str,
                 loop=asyncio.get_event_loop(),
                 timeout=60,
                 polling_pause=1):
    """
    Evaluates the given R code asynchronously and returns a CranRResult if
    we complete the task within the given time frame.
    :param source: source to evaluate.
    :param loop: loop to run on.
    :param timeout: timeout to die after (default is 1 minute)
    :param polling_pause: the rate to poll at in seconds. Defaults to 1.
    :return: CranRResult object.
    """
    async with aiohttp.ClientSession(loop=loop) as conn:
        transmit = await conn.request(
            INVOKE_REQ,
            f'{HOST}{INVOKE_EP}',
            data=json.dumps({
                'csrfmiddlewaretoken': None,  # Not sure what this is for.
                'input': source
            }))

        # Raise errors if there are any.
        transmit.raise_for_status()

        # Tells us the end point to go collect our data from.
        first_response = await transmit.json()

        if any(f not in first_response for f in ('_id', 'result')):
            raise RuntimeError(f'Unexpected response: {first_response}')

        identifier = first_response['_id']

        result_url = f'{HOST}{RETRIEVE_EP}{identifier}'

        # The job will be running in the background. We should keep checking
        # for a given period of time before giving up.
        with async_timeout.timeout(timeout):
            while True:  # Breaks by asyncio.TimeoutError eventually.
                retrieve = await conn.request(
                    RETRIEVE_REQ,
                    result_url)

                # Raise errors
                retrieve.raise_for_status()

                second_response = await retrieve.json()

                if second_response['state'] == 'complete':
                    break
                elif second_response['result'] == 'failure':
                    break
                else:
                    await asyncio.sleep(polling_pause)

        # Decipher images from base 64 into raw bytes. Yes, this is blocking,
        # but it should be a fairly fast operation to perform.
        images = []
        for image in second_response['images']:
            b64 = image['$binary']
            image_type = image['$type']  # TODO: find out what this means.
            byte_data = base64.b64decode(b64)
            images.append((byte_data, image_type))

        return CranRResult(
            second_response['failReason'],
            second_response['state'],
            second_response['result'],
            images,
            second_response['output'])


# Just like for Coliru. Unit testing time.
if __name__ == '__main__':
    source = '\n'.join((
        'library(ggplot2)',
        '',
        '# Use stdout as per normal...',
        'print("Hello, world!")',
        '',
        '# Use plots...',
        'plot(cars)',
        '',
        '# Even ggplot!',
        'qplot(wt, mpg, data=mtcars, colour=factor(cyl))',
        '',
        ''))

    result = asyncio.get_event_loop().run_until_complete(eval_r(source))
    print(result)
