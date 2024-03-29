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
"""Functions to help with searching claims in the LBRY network."""
import concurrent.futures as fts

import requests

import lbrytools.funcs as funcs


def check_repost(item, repost=True):
    """Check if the item is a repost, and return the original item.

    A claim that is just the repost of another cannot be downloaded directly,
    so we replace the input item with the original source item.

    Parameters
    ----------
    item: dict
        A dictionary with the information on an item, obtained
        from `lbrynet resolve` or `lbrynet claim search`.
    repost: bool, optional
        It defaults to `True`, in which case the returned `item`
        will be the reposted claim, that is,
        the value of `item['reposted_claim']`.
        If it's `False` it will return the original input `item`.

    Returns
    -------
    dict
        The original `item` dictionary if it is not a repost
        or if it's a repost but `repost=False`.
        Otherwise, it will return `item['reposted_claim']`.
    """
    if "reposted_claim" in item:
        old_uri = item["canonical_url"]
        uri = item["reposted_claim"]["canonical_url"]

        print("This is a repost.")
        print(f"canonical_url:  {old_uri}")
        print(f"reposted_claim: {uri}")
        print()

        if repost:
            item = item["reposted_claim"]

    return item


def search_item_uri(uri=None, repost=True,
                    print_error=True,
                    server="http://localhost:5279"):
    """Find a single item in the LBRY network, resolving the URI.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    repost: bool, optional
        It defaults to `True`, in which case it will check if the claim
        is a repost, and if it is, it will return the original claim.
        If it is `False`, it won't check for a repost, it will simply return
        the found claim.
    print_error: bool, optional
        It defaults to `True`, in which case it will print the error message
        that `lbrynet resolve` returns.
        By setting this value to `False` no messages will be printed;
        this is useful inside other functions when we want to limit
        the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the `claim`
        that was found matching the URI.
    False
        If the dictionary has the `'error'` key, it will print the contents
        of this key, and return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not uri or not isinstance(uri, str):
        m = ["Search by URI, full or partial.",
             "lbry://@MyChannel#3/some-video-name#2",
             "       @MyChannel#3/some-video-name#2",
             "                    some-video-name"]
        print("\n".join(m))
        print(f"uri={uri}")
        return False

    cmd = ["lbrynet",
           "resolve",
           uri]

    msg = {"method": cmd[1],
           "params": {"urls": uri}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    item = output["result"][uri]

    if "error" in item:
        if print_error:
            error = item["error"]
            if "name" in error:
                name_err = error["name"]
                text_err = error["text"]
                print(f">>> Error: {name_err}, {text_err}")
            else:
                print(f">>> Error: {error}")
            print(">>> Check that the URI is correct, "
                  "or that the claim hasn't been removed from the network.")
        return False

    # The found item may be a repost so we check it,
    # and return the original source item.
    item = check_repost(item, repost=repost)

    return item


def search_item_cid(cid=None, name=None,
                    repost=True, offline=False,
                    print_error=True,
                    server="http://localhost:5279"):
    """Find a single item in the LBRY network, resolving the claim id or name.

    If both `cid` and `name` are given, `cid` is used.

    Parameters
    ----------
    cid: str
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    repost: bool, optional
        It defaults to `True`, in which case it will check if the claim
        is a repost, and if it is, it will return the original claim.
        If it is `False`, it won't check for a repost, it will simply return
        the found claim.
    offline: bool, optional
        It defaults to `False`, in which case it will use
        `lbrynet claim search` to search `cid` or `name` in the online
        database.

        If it is `True` it will use `lbrynet file list` to search
        `cid` or `name` in the offline database, that is,
        in the downloaded content.
        This is required for 'invalid' claims, which have been removed from
        the online database but may still exist locally.

        When `offline=True`, `repost=True` has no effect because reposts
        must be resolved online.
    print_error: bool, optional
        It defaults to `True`, in which case it will print an error message
        if the claim is not found.
        By setting this value to `False` no messages will be printed;
        this is helpful if this function is used inside other functions,
        and we want to limit the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        Returns the dictionary that represents the `claim`
        that was found matching the `name` or `cid`.
    False
        If the dictionary seems to have no items found, it will print
        an error message and return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if (name and (not isinstance(name, str)
                  or "#" in name or ":" in name or "@" in name)
            or cid and (not isinstance(cid, str)
                        or "#" in cid or ":" in cid or "@" in cid)
            or not (name or cid)):
        m = ["Search by 'name' or 'claim_id' only.",
             "lbry://@MyChannel#3/some-video-name#2",
             "                    ^-------------^",
             "                          name"]
        print("\n".join(m))
        print(f"cid={cid}")
        print(f"name={name}")
        return False

    if offline:
        cmd = ["lbrynet",
               "file",
               "list",
               "--claim_name='{}'".format(name)]
        if cid:
            cmd[3] = "--claim_id=" + cid

        msg = {"method": cmd[1] + "_" + cmd[2],
               "params": {"claim_name": name}}
    else:
        cmd = ["lbrynet",
               "claim",
               "search",
               "--name={}".format(name)]
        if cid:
            cmd[3] = "--claim_ids=" + cid

        msg = {"method": cmd[1] + "_" + cmd[2],
               "params": {"name": name}}

    if cid:
        msg["params"] = {"claim_id": cid}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        print(">>> No 'result' in the JSON-RPC server output")
        return False

    data = output["result"]

    if "blocked" in data and data["blocked"]["total"] > 0:
        chs = data["blocked"]["channels"]
        blks = []

        for blocking in chs:
            blk = blocking["channel"]["canonical_url"].split("lbry://")[1]
            blks.append(blk)

        ch = " ; ".join(blks)

        print(">>> Claim blocked by hub.")
        print(f">>> Blocking channel: {ch}")
        return False

    if data["total_items"] < 1:
        if print_error:
            if cid:
                print(">>> No item found.")
                print(">>> Check that the claim ID is correct, "
                      "or that the claim hasn't been removed from "
                      "the network.")
            elif name:
                print(">>> No item found.")
                print(">>> Check that the name is correct, "
                      "or that the claim hasn't been removed from "
                      "the network.")
        return False

    # The list of items may include various reposts;
    # usually the last item is the oldest and thus the original.
    item = data["items"][-1]

    # The found item may be a repost so we check it,
    # and return the original source item.
    item = check_repost(item, repost=repost)

    return item


def search_item(uri=None, cid=None, name=None,
                repost=True, offline=False,
                print_error=True,
                server="http://localhost:5279"):
    """Find a single item in the LBRY network resolving URI, claim id, or name.

    If all inputs are provided, `uri` is used.
    If only `cid` and `name` are given, `cid` is used.

    Parameters
    ----------
    uri: str
        A unified resource identifier (URI) to a claim on the LBRY network.
        It can be full or partial.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            uri = '@MyChannel#3/some-video-name#2'
            uri = 'some-video-name'

        The URI is also called the `'canonical_url'` of the claim.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    repost: bool, optional
        It defaults to `True`, in which case it will check if the claim
        is a repost, and if it is, it will return the original claim.
        If it is `False`, it won't check for a repost, it will simply return
        the found claim.
    offline: bool, optional
        It defaults to `False`, in which case it will use
        `lbrynet claim search` to search `cid` or `name` in the online
        database.

        If it is `True` it will use `lbrynet file list` to search
        `cid` or `name` in the offline database, that is,
        in the downloaded content.
        This is required for 'invalid' claims, which have been removed from
        the online database but may still exist locally.

        When `offline=True`, `repost=True` has no effect because reposts
        must be resolved online. In this case, if `uri` is provided,
        and `name` is not, `uri` will be used as the value of `name`.
    print_error: bool, optional
        It defaults to `True`, in which case it will print the error message
        that `lbrynet resolve` or `lbrynet claim search` returns.
        If it is `False` no error messages will be printed;
        this is useful inside other functions when we want to limit
        the terminal output.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        The dictionary that represents the `claim` that was found
        matching `uri`, `cid` or `name`.
    False
        If there is a problem or no claim was found, it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not (uri or cid or name):
        print("Search by 'URI', 'claim_id' or 'name'.")
        print(f"uri={uri}")
        print(f"cid={cid}")
        print(f"name={name}")
        return False

    if offline:
        if uri and not name:
            name = uri

        item = search_item_cid(cid=cid, name=name,
                               repost=repost, offline=offline,
                               print_error=print_error,
                               server=server)
    else:
        if uri:
            item = search_item_uri(uri=uri,
                                   repost=repost,
                                   print_error=print_error,
                                   server=server)
        else:
            item = search_item_cid(cid=cid, name=name,
                                   repost=repost, offline=offline,
                                   print_error=print_error,
                                   server=server)

    if not item and print_error:
        print(f">>> uri={uri}")
        print(f">>> cid={cid}")
        print(f">>> name={name}")

    return item


def search_th(claim,
              server="http://localhost:5279"):
    """Method to resolve a claim using threads."""
    result = search_item(uri=claim, repost=True,
                         print_error=False,
                         server=server)

    if not result:
        result = search_item(cid=claim, repost=True,
                             print_error=False,
                             server=server)

    return {"original": claim,
            "resolved": result}


def resolve_claims(claims, threads=32,
                   server="http://localhost:5279"):
    """Resolve a list of claims, whether claim IDs or URLs are given.

    First it tries resolving the item by URL, and if that fails it tries
    by claim ID.

    Returns
    -------
    list of dict
        It returns a list of dictionaries, one for each claim
        in the input list. Each dictionary has two keys:
        - 'original': original input URL or claim ID (40-digit alphanumeric)
        - 'resolved': the resolved information of the claim, if it was found,
          or the value `False` if it was not found.

    False
        If there is a problem or non existing `file`,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    resolved = []
    n_claims = len(claims)

    servers = (server for n in range(n_claims))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            results = executor.map(search_th,
                                   claims, servers)

            resolved = list(results)  # generator to list
    else:
        for claim in claims:
            res = search_th(claim, server=server)

            resolved.append(res)

    return resolved


if __name__ == "__main__":
    s = search_item(uri="dsnt-exist")
    print()
    s = search_item(uri="LUKAS-LION---1984#b")
    print()
    s = search_item(cid="b7c7082fd52a5b932b6f08c83645ac808b6ba801")
    print()
    s = search_item(name="LUKAS-LION---1984")
    print()
    s = search_item(cid="wwwzyx")
