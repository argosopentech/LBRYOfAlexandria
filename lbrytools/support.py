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
"""Auxiliary functions for handling supports."""
import concurrent.futures as fts

import requests

import lbrytools.funcs as funcs
import lbrytools.search as srch


def search_cid_th(cid, server):
    """Wrapper to use with threads in `get_all_supports`."""
    s = srch.search_item(cid=cid, server=server)

    if not s:
        print()

    return s


def get_all_supports(threads=32,
                     server="http://localhost:5279"):
    """Get all supports in a dictionary; all, valid, and invalid.

    Returns
    -------
    dict
        A dictionary with information on the supports.
        The keys are the following:
        - 'all_supports': list with dictionaries of all supports.
          - One of the keys in every dictionary is `'resolve'`,
            which has another dictionary with the entire resolved information
            of the claim.
            For claims that are invalid, this value is simply `False`.
        - 'valid_supports': list with dictionaries of supports
          for valid claims only. It also has the `'resolve'` key.
        - 'invalid_supports': list with dictionaries of supports
          for invalid claims. The claim IDs in these dictionaries
          cannot be resolved anymore, so the `'resolve'` key
          is always `False`.
    False
        If there is a problem or no list of supports, it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    msg = {"method": "support_list",
           "params": {"page_size": 99000}}
    output = requests.post(server, json=msg).json()

    if "error" in output:
        return False

    supports = output["result"]["items"]
    n_supports = len(supports)

    if n_supports < 1:
        print(f"Supports found: {n_supports}")
        return False

    all_supports = []
    valid = []
    invalid = []

    # Iterables to be passed to the ThreadPoolExecutor
    results = []
    cids = (support["claim_id"] for support in supports)
    servers = (server for n in range(n_supports))

    if threads:
        with fts.ThreadPoolExecutor(max_workers=threads) as executor:
            # The input must be iterables
            results = executor.map(search_cid_th,
                                   cids, servers)
            results = list(results)  # generator to list
    else:
        for support in supports:
            s = search_cid_th(support["claim_id"],
                              server)
            results.append(s)

    for pair in zip(supports, results):
        support = pair[0]
        resolved = pair[1]

        support["resolved"] = resolved

        all_supports.append(support)

        if resolved:
            valid.append(support)
        else:
            invalid.append(support)

    return {"all_supports": all_supports,
            "valid_supports": valid,
            "invalid_supports": invalid}


def list_supports(claim_id=False, invalid=False,
                  combine=True, claims=True, channels=True,
                  sanitize=False,
                  threads=32,
                  file=None, fdate=False, sep=";",
                  server="http://localhost:5279"):
    """Print supported claims, the amount, and the trending score.

    Parameters
    ----------
    claim_id: bool, optional
        It defaults to `False`, in which case only the name of the claim
        is shown.
        If it is `True` the `'claim_id'` will be shown as well.
    invalid: bool, optional
        It defaults to `False`, in which case it will show all supported
        claims, even those that are invalid.
        If it is `True` it will only show invalid claims. Invalid are those
        which were deleted by their authors, so the claim (channel
        or content) is no longer available in the blockchain.
    combine: bool, optional
        It defaults to `True`, in which case the `global`, `group`, `local`,
        and `mixed` trending scores are added into one combined score.
        If it is `False` it will show the four values separately.
    claims: bool, optional
        It defaults to `True`, in which case supported non-channel claims
        will be shown.
        If it is `False` non-channel claims won't be shown.
    channels: bool, optional
        It defaults to `True`, in which case supported channels,
        which start with the `@` symbol, will be shown.
        If it is `False` channel claims won't be shown.
    sanitize: bool, optional
        It defaults to `False`, in which case it will not remove the emojis
        from the names and titles.
        If it is `True` it will remove these unicode characters.
        This option requires the `emoji` package to be installed.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to resolve claims,
        meaning claims that will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    file: str, optional
        It defaults to `None`.
        It must be a user writable path to which the summary will be written.
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
        A dictionary with information on the supports.
        The keys are the following:
        - 'all_supports': list with dictionaries of all supports.
          - One of the keys in every dictionary is `'resolve'`,
            which has another dictionary with the entire resolved information
            of the claim.
            For claims that are invalid, this value is simply `False`.
        - 'valid_supports': list with dictionaries of supports
          for valid claims only. It also has the `'resolve'` key.
        - 'invalid_supports': list with dictionaries of supports
          for invalid claims. The claim IDs in these dictionaries
          cannot be resolved anymore, so the `'resolve'` key
          is always `False`.
    False
        If there is a problem or no list of supports, it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    support_info = get_all_supports(threads=threads, server=server)

    if not support_info:
        return False

    all_supports = support_info["all_supports"]
    n_supports = len(all_supports)

    out = []

    for num, support in enumerate(all_supports, start=1):
        resolved = support["resolved"]

        if resolved:
            name = resolved["short_url"].split("lbry://")[1]
            title = resolved["short_url"].split("lbry://")[1]

            if "value" in resolved:
                title = resolved["value"].get("title", "(no title)")
        else:
            name = support["name"]
            title = "[" + support["name"] + "]"

        if sanitize:
            name = funcs.sanitize_text(name)
            title = funcs.sanitize_text(title)

        cid = support["claim_id"]
        is_channel = True if name.startswith("@") else False

        if is_channel and not channels:
            continue

        if not is_channel and not claims:
            continue

        obj = ""
        if claim_id:
            obj += f'"{cid}"' + f"{sep} "

        _name = f'"{name}"'

        if not resolved:
            _name = "[" + _name + "]"

        obj += f'{_name:60s}'

        _amount = float(support["amount"])
        amount = f"{_amount:14.8f}"

        if resolved:
            if invalid:
                continue

            meta = resolved["meta"]
            base = float(resolved["amount"])
            supp = float(meta["support_amount"])
        else:
            # The claim is invalid and no longer resolves online
            # so it doesn't have base support; the only support may be from us
            meta = {}
            base = 0
            supp = float(support["amount"])

        existing_support = base + supp

        trend_gl = meta.get("trending_global", 0)
        trend_gr = meta.get("trending_group", 0)
        trend_loc = meta.get("trending_local", 0)
        trend_mix = meta.get("trending_mixed", 0)

        combined = (trend_gl
                    + trend_gr
                    + trend_loc
                    + trend_mix)

        tr_gl = f'{trend_gl:7.2f}'
        tr_gr = f'{trend_gr:7.2f}'
        tr_loc = f'{trend_loc:7.2f}'
        tr_mix = f'{trend_mix:7.2f}'
        tr_combined = f'{combined:7.2f}'
        is_spent = support["is_spent"]

        line = f"{num:3d}/{n_supports:3d}" + f"{sep} "
        line += f"{obj}" + f"{sep} " + f"{amount}" + f"{sep} "
        line += f"{existing_support:15.8f}" + f"{sep} "

        if not is_spent:
            if combine:
                line += f"combined: {tr_combined}" + f"{sep} "
            else:
                line += f"mix: {tr_mix}" + f"{sep} "
                line += f"glob: {tr_gl}" + f"{sep} "
                line += f"grp: {tr_gr}" + f"{sep} "
                line += f"loc: {tr_loc}" + f"{sep} "
        else:
            continue

        line += f"{title}"

        out.append(line)

    funcs.print_content(out, file=file, fdate=fdate)

    return support_info


def get_base_support(uri=None, cid=None, name=None,
                     server="http://localhost:5279"):
    """Get the existing, base, and our support from a claim.

    Returns
    -------
    dict
        A dictionary with information on the support on a claim.
        The keys are the following:
        - 'canonical_url'
        - 'claim_id'
        - 'existing_support': total support that the claim has;
          this is `'base_support'` + `'old_support'`.
        - 'base_support': support that the claim has without our support.
        - 'old_support': support that we have added to this claim;
          it may be zero if this claim does not have any support from us.
    False
        If there is a problem or no list of supports, it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    item = srch.search_item(uri=uri, cid=cid, name=name, offline=False,
                            server=server)

    if not item:
        return False

    uri = item["canonical_url"]
    cid = item["claim_id"]
    name = item["name"]

    existing = float(item["amount"]) + float(item["meta"]["support_amount"])

    msg = {"method": "support_list",
           "params": {"claim_id": item["claim_id"]}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        return False

    supported_items = output["result"]["items"]
    old_support = 0

    if not supported_items:
        # Old support remains 0
        pass
    else:
        # There may be many independent supports
        for support in supported_items:
            old_support += float(support["amount"])

    base_support = existing - old_support

    return {"canonical_url": uri,
            "claim_id": cid,
            "name": name,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support}


def create_support(uri=None, cid=None, name=None,
                   amount=0.0,
                   server="http://localhost:5279"):
    """Create a new support on the claim.

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
    amount: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that will be deposited,
        whether there is a previous support or not.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'name': name of the claim.
        - 'existing_support': existing support before we add or remove ours;
          this is the sum of `base_support` and `old_support`.
        - 'base_support': existing minimum support that we do not control;
          all published claims must have a positive `base_support`.
        - 'old_support': support that we have added to this claim in the past;
          it may be zero.
        - 'new_support': new support that was successfully deposited
          in the claim, equal to `keep`.
        - 'txid': transaction ID in the blockchain that records the operation.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    supports = get_base_support(uri=uri, cid=cid, name=name,
                                server=server)

    if not supports:
        return False

    uri = supports["canonical_url"]
    claim_id = supports["claim_id"]
    c_name = supports["name"]
    existing = supports["existing_support"]
    base_support = supports["base_support"]
    old_support = supports["old_support"]

    new_support = 0.0
    t_input = 0.0
    t_output = 0.0
    t_fee = 0.0
    txid = None

    amount = abs(amount)
    msg = {"method": "support_create",
           "params": {"claim_id": claim_id,
                      "amount": f"{amount:.8f}"}}

    output = requests.post(server, json=msg).json()

    if "error" in output:
        error = output["error"]
        if "data" in error:
            print(">>> Error: {}, {}".format(error["data"]["name"],
                                             error["message"]))
        else:
            print(f">>> Error: {error}")
        print(f">>> Requested amount: {amount:.8f}")
        return False

    new_support = amount
    t_input = float(output["result"]["total_input"])
    t_output = float(output["result"]["total_output"])
    t_fee = float(output["result"]["total_fee"])
    txid = output["result"]["txid"]

    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           f"New support:      {new_support:14.8f}",
           "",
           f"Applied:          {new_support:14.8f}",
           f"total_input:      {t_input:14.8f}",
           f"total_output:     {t_output:14.8f}",
           f"total_fee:        {t_fee:14.8f}",
           f"txid: {txid}"]

    print("\n".join(out))

    return {"canonical_url": uri,
            "claim_id": claim_id,
            "name": c_name,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "new_support": new_support,
            "txid": txid}


def calculate_abandon(claim_id=None, keep=0.0,
                      server="http://localhost:5279"):
    """Actually abandon the support and get the data."""
    new_support = 0.0
    t_input = 0.0
    t_output = 0.0
    t_fee = 0.0
    txid = None

    msg = {"method": "support_abandon",
           "params": {"claim_id": claim_id}}

    if keep:
        msg["params"]["keep"] = f"{keep:.8f}"

    output = requests.post(server, json=msg).json()

    if "error" in output:
        error = output["error"]
        if "data" in error:
            print(">>> Error: {}, {}".format(error["data"]["name"],
                                             error["message"]))
        else:
            print(f">>> Error: {error}")
        print(f">>> Requested amount: {keep:.8f}")
        return False

    new_support = keep
    t_input = float(output["result"]["total_input"])
    t_output = float(output["result"]["total_output"])
    t_fee = float(output["result"]["total_fee"])
    txid = output["result"]["txid"]

    text = [f"Applied:          {new_support:14.8f}",
            f"total_input:      {t_input:14.8f}",
            f"total_output:     {t_output:14.8f}",
            f"total_fee:        {t_fee:14.8f}",
            f"txid: {txid}"]

    return {"new_support": new_support,
            "t_input": t_input,
            "t_output": t_output,
            "t_fee": t_fee,
            "txid": txid,
            "text": text}


def abandon_support(uri=None, cid=None, name=None,
                    keep=0.0,
                    server="http://localhost:5279"):
    """Abandon a support, or change it to a different amount.

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
    keep: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that should remain in the claim
        after we remove our previous support. That is, we can use
        this parameter to assign a new support value.
        If it is `0.0` all support is removed.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'name': name of the claim.
        - 'existing_support': existing support before we add or remove ours;
          this is the sum of `base_support` and `old_support`.
        - 'base_support': existing minimum support that we do not control;
          all published claims must have a positive `base_support`.
        - 'old_support': support that we have added to this claim in the past;
          it may be zero.
        - 'new_support': new support that was successfully deposited
          in the claim, equal to `keep`.
        - 'txid': transaction ID in the blockchain that records the operation.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    supports = get_base_support(uri=uri, cid=cid, name=name,
                                server=server)

    if not supports:
        return False

    uri = supports["canonical_url"]
    claim_id = supports["claim_id"]
    c_name = supports["name"]
    existing = supports["existing_support"]
    base_support = supports["base_support"]
    old_support = supports["old_support"]

    calculation = calculate_abandon(claim_id=claim_id, keep=keep,
                                    server=server)
    if not calculation:
        return False

    new_support = calculation["new_support"]
    txid = calculation["txid"]

    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           f"New support:      {keep:14.8f}",
           ""]
    out += calculation["text"]

    print("\n".join(out))

    return {"canonical_url": uri,
            "claim_id": claim_id,
            "name": c_name,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "new_support": new_support,
            "txid": txid}


def abandon_support_inv(invalids=None, cid=None, name=None,
                        keep=0.0,
                        threads=32,
                        server="http://localhost:5279"):
    """Abandon or change a support for invalid claims.

    Parameters
    ----------
    invalids: list of dict, optional
        A list where each element is a dictionary indicating the support
        for an 'invalid' claim.
        Invalid claims no longer resolve online (the output has been spent)
        but they may still have an existing support.
        If this list is `None`, the list will be obtained
        from `get_all_supports()['invalid_supports']`.
    cid: str, optional
        A `'claim_id'` for a claim on the LBRY network.
        It is a 40 character alphanumeric string.
    name: str, optional
        A name of a claim on the LBRY network.
        It is normally the last part of a full URI.
        ::
            uri = 'lbry://@MyChannel#3/some-video-name#2'
            name = 'some-video-name'
    keep: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that should remain in the claim
        after we remove our previous support. That is, we can use
        this parameter to assign a new support value.
        If it is `0.0` all support is removed.
    threads: int, optional
        It defaults to 32.
        It is the number of threads that will be used to resolve claims,
        meaning claims that will be searched in parallel.
        This number shouldn't be large if the CPU doesn't have many cores.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim, which will be `None`
          because the claim can't be resolved online any more.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'name': name of the claim.
        - 'existing_support': existing support before we add or remove ours;
          this should be the same as `old_support`.
        - 'base_support': since this claim does not resolve any more,
          it should be zero.
        - 'old_support': support that we have added to this claim in the past;
          it cannot be zero because we use this method only with claims
          that have been previously supported (and are now invalid).
        - 'new_support': new support that was successfully deposited
          in the claim, equal to `keep`.
        - 'txid': transaction ID in the blockchain that records the operation.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    if not cid and not name:
        print(80 * "-")
        print(f'cid={cid}\n'
              f'name="{name}"')
        return False

    existing = 0
    base_support = 0
    old_support = 0
    found = False

    if not invalids:
        support_info = get_all_supports(threads=threads, server=server)

        if not support_info:
            return False

        invalids = support_info["invalid_supports"]

    for support in invalids:
        if ((cid and cid in support["claim_id"])
                or (name and name in support["name"])):
            existing = float(support["amount"])
            old_support = float(support["amount"])
            claim_id = support["claim_id"]
            c_name = support["name"]
            found = True

    if not found:
        print(80 * "-")
        print("Claim not found among the invalid claims")
        print(f'cid={cid}\n'
              f'name="{name}"')
        return False

    calculation = calculate_abandon(claim_id=claim_id, keep=keep,
                                    server=server)
    if not calculation:
        return False

    new_support = calculation["new_support"]
    txid = calculation["txid"]

    out = [f"claim_name: {c_name}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           f"New support:      {keep:14.8f}",
           ""]
    out += calculation["text"]

    print("\n".join(out))

    return {"canonical_url": None,
            "claim_id": claim_id,
            "name": c_name,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "new_support": new_support,
            "txid": txid}


def target_support(uri=None, cid=None, name=None,
                   target=0.0,
                   server="http://localhost:5279"):
    """Add an appropriate amount of LBC to reach a target support.

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
    target: float, optional
        It defaults to `0.0`.
        It is the amount of LBC support that we want the claim to have
        at the end of our support.
        For example, if the current support is `100`, and we specify a target
        of `500`, we will be supporting the claim with `400`
        in order to reach the target.
    server: str, optional
        It defaults to `'http://localhost:5279'`.
        This is the address of the `lbrynet` daemon, which should be running
        in your computer before using any `lbrynet` command.
        Normally, there is no need to change this parameter from its default
        value.

    Returns
    -------
    dict
        A dictionary with information on the result of the support.
        The keys are the following:
        - 'canonical_url': canonical URI of the claim.
        - 'claim_id': unique 40 character alphanumeric string.
        - 'name': name of the claim.
        - 'existing_support': existing support before we add or remove ours;
          this is the sum of `base_support` and `old_support`.
        - 'base_support': existing minimum support that we do not control;
          all published claims must have a positive `base_support`.
        - 'old_support': support that we have added to this claim in the past;
          it may be zero.
        - 'target': target support that we want after running this method.
          It must be a positive number.
        - 'must_add': amount of support that we must add or remove (negative)
          to reach the `target`; it may be zero if `target`
          is already below the `base_support`.
        - 'new_support': new support that was successfully deposited
          in the claim; it may be zero if `target` is already below
          the `base_support`, or if `old_support` already satisfies
          our `target`.
        - 'txid': transaction ID in the blockchain that records the operation;
          it may be `None` if the transaction was not made because the `target`
          was already achieved before applying additional support.
    False
        If there is a problem or non existing claim, or lack of funds,
        it will return `False`.
    """
    if not funcs.server_exists(server=server):
        return False

    supports = get_base_support(uri=uri, cid=cid, name=name,
                                server=server)

    if not supports:
        return False

    uri = supports["canonical_url"]
    claim_id = supports["claim_id"]
    c_name = supports["name"]
    existing = supports["existing_support"]
    base_support = supports["base_support"]
    old_support = supports["old_support"]

    target = abs(target)
    out = [f"canonical_url: {uri}",
           f"claim_id: {claim_id}",
           f"Existing support: {existing:14.8f}",
           f"Base support:     {base_support:14.8f}",
           f"Old support:      {old_support:14.8f}",
           "",
           f"Target:           {target:14.8f}"]

    new_support = 0.0
    must_add = 0.0

    if target > base_support:
        # Target above base, calculate addition
        must_add = target - existing
        new_support = old_support + must_add
    elif target < base_support:
        if not old_support:
            # Target below base support, and no old support, nothing to add,
            # reset support to 0
            pass
        else:
            # Target below base support, and old support, remove it
            must_add = -old_support
    else:
        # Same target as base support, nothing to add, reset support to 0
        pass

    out.append(f"Must add:         {must_add:14.8f}")
    out.append(f"New support:      {new_support:14.8f}")

    applied = 0.0
    t_input = 0.0
    t_output = 0.0
    t_fee = 0.0
    txid = None

    # The SDK accepts the amount as a string, not directly as a number.
    # The minimum amount is 0.00000001, so we convert all quantities
    # to have 8 decimal significant numbers.
    #
    # Only perform the transaction if the new support is different
    # from the old support
    if new_support != old_support:
        if not old_support and new_support > 0:
            # No existing support, so we create it
            msg = {"method": "support_create",
                   "params": {"claim_id": claim_id,
                              "amount": f"{new_support:.8f}"}}
            output = requests.post(server, json=msg).json()
        else:
            # Existing support, so we update it with the new value
            msg = {"method": "support_abandon",
                   "params": {"claim_id": claim_id,
                              "keep": f"{new_support:.8f}"}}
            output = requests.post(server, json=msg).json()

        if "error" in output:
            error = output["error"]
            if "data" in error:
                print(">>> Error: {}, {}".format(error["data"]["name"],
                                                 error["message"]))
            else:
                print(f">>> Error: {error}")
            print(f">>> Requested amount: {new_support:.8f}")
            return False

        applied = new_support
        t_input = float(output["result"]["total_input"])
        t_output = float(output["result"]["total_output"])
        t_fee = float(output["result"]["total_fee"])
        txid = output["result"]["txid"]

    out += ["",
            f"Applied:          {applied:14.8f}",
            f"total_input:      {t_input:14.8f}",
            f"total_output:     {t_output:14.8f}",
            f"total_fee:        {t_fee:14.8f}",
            f"txid: {txid}"]

    print("\n".join(out))

    return {"canonical_url": uri,
            "claim_id": cid,
            "name": c_name,
            "existing_support": existing,
            "base_support": base_support,
            "old_support": old_support,
            "target": target,
            "must_add": must_add,
            "new_support": new_support,
            "txid": txid}
