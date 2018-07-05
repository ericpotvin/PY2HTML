#!/usr/bin/python

""" Generate website
"""
from collections import OrderedDict
from datetime import datetime
from shutil import copyfile

import pytz

from website import create_page, generate_sitemap, generate_rss, get_page_info, is_feed
from website import SOURCE_DIR
from website import PAGE_FILE, VERSION_DIR, HTML_DIR

import os

#
# Start the engine
#

tz = pytz.timezone('America/Los_Angeles')

sitemap_urls = OrderedDict()
rss_urls = OrderedDict()

for folder, subs, files in os.walk(SOURCE_DIR):

    map_folder = folder.replace(SOURCE_DIR, "")

    file_time = int(os.path.getmtime(folder + "/" + PAGE_FILE))

    # sitemap
    sitemap_data = dict()
    sitemap_data['url'] = map_folder
    sitemap_data['priority'] = 1 - (map_folder.count("/") * 0.15)
    sitemap_data['date'] = datetime.fromtimestamp(
        file_time
        , tz
    ).isoformat(' ')

    if map_folder not in sitemap_urls:
        sitemap_urls[map_folder] = dict()
    sitemap_urls[map_folder] = sitemap_data

    # rss
    if is_feed(map_folder):
        rss_data = dict()
        rss_data['url'] = map_folder
        item = get_page_info(SOURCE_DIR + "/" + map_folder + "/" + PAGE_FILE, 0)

        rss_data['title'] = item['title']
        rss_data['desc'] = item['desc']

        rss_urls[map_folder] = rss_data

    with open(os.path.join(folder, PAGE_FILE), 'r') as destination:
        for filename in files:
            if filename != PAGE_FILE:
                continue

            if os.path.isfile(folder + "/" + PAGE_FILE):
                create_page(folder, filename)

# Copy the 404 page
copyfile(VERSION_DIR + "404.html", HTML_DIR + "404.html")

generate_sitemap(sorted(sitemap_urls.items()))

generate_rss(sorted(rss_urls.items()))
