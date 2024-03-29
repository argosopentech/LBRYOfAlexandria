#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2021 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining       #
# a copy of this software and associated documentation files                  #
# (the "Software"), to deal in the Software without restriction, including    #
# without limitation the rights to use, copy, modify, merge, publish,         #
# distribute, sublicense, and/or sell copies of the Software, and to permit   #
# persons to whom the Software is furnished to do so, subject to the          #
# following conditions:                                                       #
#                                                                             #
# The above copyright notice and this permission notice shall be included     #
# in all copies or substantial portions of the Software.                      #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
# --------------------------------------------------------------------------- #
"""Functions to manipulate the claims found in the network.

These methods are used with lists of claims returned by `claim_search`.
"""


def sort_and_filter(claims, number=0, reverse=False):
    """Sort the input list and remove duplicated items with same claim ID.

    Parameters
    ----------
    claims: list of dict
        List of claims obtained from `claim_search`.
    number: int, optional
        It defaults to 0, in which case the returned list will contain
        all unique claims.
        If this is any other number, it will cut the output list to have
        a maximum of `number` claims.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the output list.
        If it is `True` the newest items will come first in the output list.

    Returns
    -------
    list of dict
        List of claims obtained from `claim_search`, with the duplicates
        removed.
    """
    print("Sort claims and remove duplicates")
    new_items = []
    n_claims = len(claims)

    # Make sure the `release_time` exists, and use `timestamp` otherwise
    for num, claim in enumerate(claims, start=1):
        if "release_time" not in claim["value"]:
            name = claim["name"]
            print(f'{num:4d}/{n_claims:4d}; "{name}" using "timestamp"')
            claim["value"]["release_time"] = claim["timestamp"]
        new_items.append(claim)

    # Sort by using the original `release_time`.
    # New items will come first.
    sorted_items = sorted(new_items,
                          key=lambda v: int(v["value"]["release_time"]),
                          reverse=True)

    unique_ids = []
    unique_claims = []

    for item in sorted_items:
        if item["claim_id"] not in unique_ids:
            unique_claims.append(item)
            unique_ids.append(item["claim_id"])

    if number:
        # Cut the older items
        unique_claims = unique_claims[0:number]

    if not reverse:
        # Invert the list so that older items appear first
        unique_claims.reverse()

    return unique_claims


def downloadable_size(claims, local=False, print_msg=True):
    """Calculate the total size of input claims.

    Parameters
    ----------
    claims: list of dict
        List of claims obtained from `claim_search`,
        or if using `local=True`, from `file_list`.
    local: bool, optional
        It defaults to `False` in which case it assumes the claims
        were resolved online from `claim_search`.
        If it is `True` it assumes the claims come from `file_list`,
        that is, from the claims locally downloaded.
        This is necessary because the information is in different fields
        depending on where it comes from.

    Returns
    -------
    dict
        A dictionary with eight keys:
        - 'size': total size of the claims in bytes.
          It can be divided by 1024 to obtain kibibytes, by another 1024
          to obtain mebibytes, and by another 1024 to obtain gibibytes.
        - 'duration': total duration of the claims in seconds.
          It will count only stream types which have a duration
          such as audio and video.
        - 'size_GB': total size in GiB (floating point value)
        - 'd_h': integer hours HH when the duration is shown as HH:MM:SS
        - 'd_min': integer minutes MM when the duration is shown as HH:MM:SS
        - 'd_s`: integer seconds SS when the duration is shown as HH:MM:SS
        - 'days': total seconds converted into days (floating point value)
        - 'summary': paragraph of text describing the number of claims,
           the total size in GiB, and the total duration expressed as HH:MM:SS,
           and days
    """
    if print_msg:
        if local:
            print("Calculate size of fully downloaded claims")
        else:
            print("Calculate size of downloadable claims")

    n_claims = len(claims)
    total_bytes = 0
    total_seconds = 0

    for num, claim in enumerate(claims, start=1):
        if local:
            vtype = claim["mime_type"]
            source_info = claim["metadata"]
            alt_name = claim["stream_name"]
        else:
            vtype = claim["value_type"]
            source_info = claim["value"]
            alt_name = claim["name"]

        if "source" in source_info:
            file_name = source_info["source"].get("name", "None")
            size = int(source_info["source"].get("size", 0))
        else:
            file_name = alt_name
            size = 0
            if print_msg:
                print(f"{num:4d}/{n_claims:4d}; type: {vtype}; "
                      f'no source: "{file_name}"')

        seconds = 0
        if "video" in source_info:
            seconds = source_info["video"].get("duration", 0)
        elif "audio" in source_info:
            seconds = source_info["audio"].get("duration", 0)

        total_bytes += size
        total_seconds += seconds

    size_gb = total_bytes / (1024**3)
    hrs = total_seconds / 3600
    days = hrs / 24

    hr = total_seconds // 3600
    mi = (total_seconds % 3600) // 60
    sec = (total_seconds % 3600) % 60

    m = [f"Claims: {n_claims}",
         f"Total size: {size_gb:.4f} GB",
         f"Total duration: {hr} h {mi} min {sec} s, "
         f"or {days:.4f} days"]

    summary = "\n".join(m)

    return {"size": total_bytes,
            "duration": total_seconds,
            "size_GB": size_gb,
            "d_h": hr,
            "d_min": mi,
            "d_s": sec,
            "days": days,
            "summary": summary}


def sort_filter_size(claims, number=0, reverse=False,
                     print_msg=False):
    """Sort, filter the claims, and provide the download size and duration.

    Parameters
    ----------
    claims: list of dict
        List of claims obtained from `claim_search`.
    number: int, optional
        It defaults to 0, in which case the returned list will contain
        all unique claims.
        If this is any other number, it will cut the output list to have
        a maximum of `number` claims.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        on the output list.
        If it is `True` the newest items will come first in the output list.
    print_msg: bool, optional
        It defaults to `False`.
        If it `True` it will print the summary information.

    Returns
    -------
    dict
        A dictionary with nine keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `claim_search`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (new claims first) if `reverse=True`.
        - The other eight keys are the same from `downloadable_size`,
          'size', 'duration', 'size_GB', 'd_h', 'd_min', 'd_s', 'days',
          and 'summary'.
    """
    claims = sort_and_filter(claims, number=number, reverse=reverse)

    print()
    claims_info = downloadable_size(claims)

    if print_msg:
        print(40 * "-")
        print(claims_info["summary"])

    claims_info["claims"] = claims

    return claims_info
