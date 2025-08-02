#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'bluesky_2_album'

import yaml
from telegram_util import AlbumResult as Result
from telegram_util import compactText, matchKey
import json
import html
import cached_url
from atproto import Client, models, IdResolver
import os

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)
os.system('mkdir tmp > /dev/null 2>&1')

resolver = IdResolver()

bluesky_client_cache = {}
def getClient():
    if 'bluesky_client' in bluesky_client_cache:
        return bluesky_client_cache['bluesky_client']
    client = Client()
    client.login(credential['bluesky_user'], credential['bluesky_password'])
    bluesky_client_cache['bluesky_client'] = client
    return client

def getText(record):
    text = list(record.text)
    for facet in (record.facets or []):
        uri = None
        for feature in facet.features:
            try:
                uri = feature.uri
                break
            except:
                ...
        if not uri:
            continue
        count = 0
        for i , a in enumerate(text[:]):
            if count == facet.index.byte_start:
                text[i] = ('<a href="%s">' % uri) + text[i]
            count += len(a.encode('utf-8'))
            if count == facet.index.byte_end:
                text[i] += '</a>'
    return ''.join(text)

def getFakeUrlFromRef(ref):
    try:
        return ref.link
    except:
        return ref

def getImages(client, record, did):
    media_list = []
    try:
        media_list.append(record.embed.video)
    except:
        ...
    try:
        media_list.append(record.embed.media.video)
    except:
        ...
    try:
        media_list += [x.image for x in record.embed.images]
    except:
        ...
    try:
        media_list += [x.image for x in record.embed.media.images]
    except:
        ...
    result = []
    if not media_list:
        return []
    for media in media_list:
        url = getFakeUrlFromRef(media.ref)
        result.append('https://bsky.social/xrpc/com.atproto.sync.getBlob?did=%s&cid=%s' % (did, url))
        # result.append(url)
        # fn = cached_url.getFilePath(url)
        # blob = client.com.atproto.sync.get_blob(params={'cid':url, 'did': did})
        # with open(fn,'w') as f:
        #     f.write(blob)
    return result

def _get(client, path):
    result = Result()
    result.url = path
    post = client.get_post(path.split('/')[-1], path.split('/')[-3])
    record = post.value
    result.cap_html_v2 = getText(record)
    try:
        did = resolver.handle.resolve(path.split('/')[-3])
    except:
        did = path.split('/')[-3]
    result.imgs = getImages(client, record, did)
    try:
        quoted_path = record.embed.record.uri
    except:
        return result
    quoted_result = _get(client, quoted_path)
    result.imgs += quoted_result.imgs
    if quoted_result.cap_html_v2:
        if not result.cap_html_v2:
            result.cap_html_v2 = quoted_result.cap_html_v2
        else:
            result.cap_html_v2 = quoted_result.cap_html_v2 + '\n\n【网评】' + result.cap_html_v2
    return result

def get(path):
    return _get(getClient(), path)