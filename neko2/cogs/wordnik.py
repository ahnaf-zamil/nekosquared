#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Wordnik support.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import functools
import typing
import urllib.error

# The API poops out XML tags.
import bs4
from discord import embeds
from wordnik import WordApi, swagger

from discomaton import book
from neko2.shared import alg, commands, configfiles, errors, traits

config_file = "wordnik"

wordnik_endpoint = "http://api.wordnik.com/v4"


def deswagger(node):
    """Unravels the swagger types into Python primitives.."""
    if node is not None and hasattr(node, "swaggerTypes"):
        data = {st: deswagger(getattr(node, st, None)) for st in node.swaggerTypes}
        return data
    elif isinstance(node, str):
        # Remove XML.
        soup = bs4.BeautifulSoup(node)
        return soup.text
    elif isinstance(node, (set, list, tuple, frozenset)):
        # Deswagger and remove Nones.
        return [deswagger(m) for m in node if m is not None]
    elif isinstance(node, dict):
        # Deswagger and remove None values.
        return {k: deswagger(v) for k, v in node.items() if v is not None}
    else:
        return node


def rank_d(name):
    """Helper for ranking dictionaries. A smaller number is better."""
    if name == "gcide":
        return 0
    elif name == "wordnet":
        return 1
    elif name == "ahd":
        return 3
    else:
        return 2


def sorting_key(word: dict):
    """
    A function that returns some sortable quantity from the given word.

    This is done to make certain dictionaries take precedence, as they
    seem to be better in my experience.
    """
    return f'{rank_d(word["sourceDictionary"])}{word["word"].lower()}'


def ellipse(text: str, maximum=1024) -> typing.Optional[str]:
    if not text:
        return embeds.EmptyEmbed
    return text[: maximum - 3] + "..." if len(text) > maximum else text


def quote(text: str):
    if not text:
        return text

    def pred(x, y=None):
        if not y:
            y = x
        return text.startswith(x) and text.endswith(y)

    if any(pred(x) for x in ('"', "'", ("‘", "’"), ("“", "”"))):
        text = text[1:-1]

    # Ensure capitalised start
    text = f"{text[0:1].upper()}{text[1:]}"
    if not any(text.endswith(x) for x in ("!", "?", ".", ",")):
        text += "."

    return f"“{text}”"


class WordnikCog(traits.CogTraits):
    """
    Wordnik support cog. Allows searching for words through a selection
    of online dictionaries.
    """

    def __init__(self):
        self._token = configfiles.get_config_data(config_file)
        self.api_client = swagger.ApiClient(self._token, wordnik_endpoint)
        self.api = WordApi.WordApi(self.api_client)

    async def _lookup(self, phrase: str) -> typing.List[dict]:
        """Executes the lookup in a thread pool to prevent blocking."""

        partial = functools.partial(
            self.api.getDefinitions,
            phrase,
            sourceDictionaries="all",
            includeRelated=True,
            useCanonical=True,
            includeTags=True,
        )

        try:
            results = await self.run_in_io_executor(partial)
            if not isinstance(results, list):
                raise errors.NotFound("No result was found.")
            else:
                # Remove XML, convert to dict, as this is easier to look at.
                for i, result in enumerate(results):
                    results[i] = deswagger(result)

            results.sort(key=sorting_key)

        except urllib.error.HTTPError:
            raise errors.NotFound("No result was found.")
        else:
            return results

    @commands.group(
        brief="Looks up phrases in online dictionaries",
        invoke_without_command=True,
        aliases=["def"],
    )
    async def define(self, ctx, *, phrase: str):

        try:
            with ctx.typing():
                results: typing.List[dict] = await self._lookup(phrase)
        except errors.NotFound as ex:
            return await ctx.send(str(ex), delete_after=10)

        pages = []

        for result in results:
            extended_text = ellipse(result.get("extendedText", None))
            source = result.get("attributionText", result["sourceDictionary"])
            citations = [
                f'{quote(c["cite"])} - {c["source"]}'
                for c in result.get("citations", [])
                if c["cite"]
            ]
            citations = ellipse("\n\n".join(citations))
            examples = [e["text"] for e in result.get("exampleUses", [])]
            # Capitalise each example, and quote it.
            examples = [quote(e) for e in examples]
            examples = ellipse("\n\n".join(examples))
            title = result["word"].upper()
            part_of_speech = result.get("partOfSpeech", None)
            definition = result.get("text", "_No definition_")
            if part_of_speech:
                definition = "**" + part_of_speech + "**: " + definition
            definition = ellipse(definition, 2000)

            # Maps relation type to sets of words.
            related = {}
            for rel_word in result.get("relatedWords", []):
                rwl = related.setdefault(rel_word["relationshipType"], set())
                for word in rel_word["words"]:
                    rwl.add(word.title())

            embed = embeds.Embed(
                title=title, description=definition, colour=alg.rand_colour()
            )

            embed.set_footer(text=source)

            if extended_text:
                embed.add_field(name="Extended definition", value=extended_text)

            if citations:
                embed.add_field(name="Citations", value=citations)

            if examples:
                embed.add_field(name="Examples", value=examples)

            if related:
                for relation, words in related.items():
                    embed.add_field(name=f"{relation}s".title(), value=", ".join(words))

            pages.append(embed)

        book.EmbedBooklet(ctx=ctx, pages=pages).start()


def setup(bot):
    bot.add_cog(WordnikCog())
