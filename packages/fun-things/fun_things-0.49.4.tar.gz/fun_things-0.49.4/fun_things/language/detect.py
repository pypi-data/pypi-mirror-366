# import unicodedata
# import regex

import pycountry

from .payload import Payload

try:
    import pycld2
except Exception:
    pycld2 = None

try:
    import langdetect
except Exception:
    langdetect = None

# RE_BAD_CHARS = regex.compile(r"\p{Cc}|\p{Cs}")


# def _remove_bad_chars(text):
#     text = "".join(
#         [
#             l
#             for l in text
#             if unicodedata.category(str(l))[0]
#             not in (
#                 "S",
#                 "M",
#                 "C",
#             )
#         ]
#     )
#     return RE_BAD_CHARS.sub("", text)


def _parse_pycld2(text: str):
    if pycld2 is None:
        return

    try:
        isReliable, textBytesFound, details, vectors = pycld2.detect(
            text, returnVectors=True
        )

        for info in details:
            name, code, percent, score = info

            if name != "Unknown" and percent > 0:
                yield Payload(
                    name=name,
                    code=code,
                    percent=percent / 100,
                    source="pycld2",
                )

    except Exception:
        pass


def _parse_langdetect(text: str):
    if langdetect is None:
        return

    langs = langdetect.detect_langs(text)

    for lang in langs:
        pycountry_lang = pycountry.languages.get(
            alpha_2=lang.lang,
        )

        if pycountry_lang is None:
            continue

        yield Payload(
            name=pycountry_lang.name.upper(),
            code=lang.lang,
            percent=lang.prob,
            source="langdetect",
        )


def detect(text: str):
    """
    Requires `pycld2` or `langdetect`, or both.
    """
    if text is None:
        return []

    # text = _remove_bad_chars(text)

    from_pycld2 = list(_parse_pycld2(text))

    if any(from_pycld2):
        return from_pycld2

    return list(_parse_langdetect(text))
