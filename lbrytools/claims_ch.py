#!/usr/bin/env python3
# --------------------------------------------------------------------------- #
# The MIT License (MIT)                                                       #
#                                                                             #
# Copyright (c) 2022 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>       #
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
"""Functions to print claims of a channel."""
import lbrytools.funcs as funcs
import lbrytools.search_ch_all as srchall
import lbrytools.print_claims as prntc


def list_ch_claims(channel,
                   number=0,
                   create=False, height=False, release=True,
                   claim_id=False, typ=True, ch_name=False,
                   sizes=True, supports=True, fees=True,
                   title=False, sanitize=False,
                   start=1, end=0,
                   reverse=False,
                   last_height=99_000_900,
                   file=None, fdate=False, sep=";",
                   server="http://localhost:5279"):
    """Print the claims from a single clannel.

    Parameters
    ----------
    channel: str
        Channel for which to show claims.
    number: int, optional
        It defaults to 0, in which case the returned list will contain
        all unique claims.
        If this is any other number, it return only the newest claims
        up to an including `number`.
    create: bool, optional
        It defaults to `False`.
        If it is `True` it will print the creation height and creation time
        of each claim.
    height: bool, optional
        It defaults to `False`.
        If it is `True` it will print the block height and timestamp
        of each claim.
    release: bool, optional
        It defaults to `True`, in which case it will print the release time
        of each claim.
    claim_id: bool, optional
        It defaults to `False`.
        If it is `True` it will print the claim ID (40-character string).
    typ: bool, optional
        It defaults to `True`, in which case it will print the value type
        of the claim, and if applicable (for stream claims)
        the stream type and the media type.
    ch_name: bool, optional
        It defaults to `False`.
        If it is `True` it will print the channel name that published
        the claim.
    sizes: bool, optional
        It defaults to `True`, in which case it will print the duration
        in minutes and seconds, and size in MB of each claim, if applicable
        (streams of type `'audio'` and `'video'`).
    supports: bool, optional
        It defaults to `True`, in which case it will print the total LBC
        supporting the claim; this is the sum of the author's amount
        and support amount.
    fees: bool, optional
        It defaults to `True`, in which case it will print the fee (quantity
        and currency) associated with accessing each claim, if applicable.
    title: bool, optional
        It defaults to `False`, in which case the claim `'name'`
        will be printed.
        If it is `True` it will print the claim `'title'` instead.
        To download a stream, the claim name or the claim ID must be used.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the name of the claim and channel.
        If it is `True` it will remove these unicode characters
        and replace them with a simple black square.
        This option requires the `emoji` package to be installed.
    start: int, optional
        It defaults to 1.
        Show claims starting from this index in the list of items.
    end: int, optional
        It defaults to 0.
        Show claims until and including this index in the list of items.
        If it is 0, it is the same as the last index in the list.
    reverse: bool, optional
        It defaults to `False`, in which case older items come first
        in the printed output list.
        If it is `True` newer claims are at the beginning of the list.
    last_height: int, optional
        Last block used to find claims.
        It will find claims in blocks before this block height, therefore,
        to find all claims this value must be larger than the last block
        in the blockchain at present time.
        The default value will have to be increased if the blockchain
        ever reaches this value, although this is unlikely in the short term.
    file: str, optional
        It defaults to `None`.
        It must be a writable path to which the summary will be written.
        Otherwise the summary will be printed to the terminal.
    fdate: bool, optional
        It defaults to `False`.
        If it is `True` it will add the date to the name of the summary file.
    sep: str, optional
        It defaults to `;`. It is the separator character between
        the data fields in the printed summary. Since the claim name
        can have commas, a semicolon `;` is used by default.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with nine keys:
        - 'claims': a list of dictionaries where every dictionary represents
          a claim returned by `claim_search`.
          The list is ordered in ascending order by default (old claims first),
          and in descending order (newer claims first) if `reverse=True`.
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
    False
        It there is a problem it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not channel.startswith("@"):
        channel = "@" + channel

    if number:
        claims_info = srchall.ch_search_n_claims(channel,
                                                 number=number,
                                                 last_height=last_height,
                                                 reverse=False,
                                                 server=server)
    else:
        claims_info = srchall.ch_search_all_claims(channel,
                                                   last_height=last_height,
                                                   reverse=False,
                                                   server=server)

    if claims_info["claims"]:
        print()
        prntc.print_sch_claims(claims_info["claims"],
                               create=create, height=height, release=release,
                               claim_id=claim_id, typ=typ, ch_name=ch_name,
                               long_chan=False,
                               sizes=sizes, supports=supports, fees=fees,
                               title=title, sanitize=sanitize,
                               start=start, end=end,
                               reverse=reverse,
                               file=file, fdate=fdate, sep=sep)

    print(80 * "-")
    print(claims_info["summary"])

    return claims_info


if __name__ == "__main__":
    output = list_ch_claims("@AlisonMorrow")  # ~722
    print()
    output = list_ch_claims("@rossmanngroup")  # ~3152
