# -*- coding: utf-8 -*-

from urllib import parse, request
from bs4 import BeautifulSoup
import requests
import logging
import asyncio
import hangups
from Core.Commands.Dispatcher import DispatcherSingleton
import random


log = logging.getLogger(__name__)
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"}

random_for = (
    'cat',
    'cats',
    'kitty',
    'dog',
    'puppy'
    )


@DispatcherSingleton.register
def img(bot, event, *args):
    """
    **Img:**
    Usage: /img <search term>
    Purpose: Sends the first thumbnail for the search term in google image search.
    """
    log.info('/img from {}: {}'.format(event.user.full_name, ' '.join(args)))
    global headers

    query = ' '.join(args)
    if query.lower() in random_for:
        random.seed()
        first = randint(2, 1000000)
    else:
        first = 2

    url = 'https://www.bing.com/images/async?{}&async=content&first={}'.format(parse.urlencode({'q': query}), first)
    response = requests.get(url, headers)
    if response.status_code != 200:
        log.error('Error searching for image')
        return

    result = response.content.decode()
    soup = BeautifulSoup(result, "html.parser")
    imgs = soup.find_all("a", title="View image details")

    if len(imgs) == 0:
        bot.send_message(event.conv, 'No images found for "{}"'.format(query))
    else:
        i = random.randint(0, len(imgs) - 1)
        a = imgs[i]['m']
        b = a.split('imgurl:"')
        c = b[1].split('"')
        url = c[0]
        yield from send_image(bot, event, url)


@asyncio.coroutine
def send_image(bot, event, url):
    try:
        image_id = yield from bot.upload_image(url)
    except HTTPError:
        log.error('Error uploading image.')
        return
    bot.send_message_segments(event.conv, [hangups.ChatMessageSegment("Picture Message")], image_id=image_id)