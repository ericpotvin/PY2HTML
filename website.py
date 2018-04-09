# coding=utf-8
""" Website Library
"""

from ConfigParser import SafeConfigParser
from datetime import date
from jinja2 import Template

import collections
import codecs
import datetime
import os
import sys
import signal


def signal_handler(sig, frame):
    """ Catch the CTRL+C signal
        :param sig: the signal
        :param frame: the frame
    """
    print '\nAborted: SIG: ' + str(sig) + " - frame:" + str(frame)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

reload(sys)

# Enable debug mode (all the print)
DEBUG = 0

PARSER = SafeConfigParser()

#
# Make sure we have a valid folder
#

if len(sys.argv) < 2:
    sys.exit("Error: no input folder specified")

# check if folder exists

#
# Functions
#


def create_page(folder, filename):
    """ Create the web page
        :param folder: the folder name
        :param filename: the filename
    """
    page_type = get_type(folder)
    canonical_folder = folder.replace(SOURCE_DIR, "")
    save_folder = HTML_DIR + canonical_folder
    save_file = save_folder + "/" + PAGE_INDEX

    if DEBUG:
        print "------------------------"
        print "(create_page) folder: " + folder
        print "(create_page) filename: " + filename
        print "(create_page) page_type : " + page_type
        print "(create_page) save_folder: " + save_folder
        print "(create_page) save_file: " + save_file

    # Create folder
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Get the HTML

    content = get_page_content(folder, page_type)
    year = date.today().year

    # Get the page details
    page = get_page_info(folder + "/" + PAGE_FILE, 0)

    # Render template
    template = Template(TEMPLATE_DATA)
    tpl = template.render(
        SITE_NAME=SITENAME,
        PAGE_TITLE=page['title'],
        PAGE_DESCRIPTION=page['desc'],
        SITE_URL=SITEURL,
        PAGE=content,
        YEAR=year,
        FOLDER=canonical_folder,
        MENU=get_menu(canonical_folder)
    )

    if DEBUG:
        print "Saving: " + save_file
    else:
        print ".",

    with codecs.open(save_file, "w", "utf8") as file_save:
        file_save.write(tpl)


def get_config_info():
    """ Get the config / settings for the website
    """

    if not os.path.isfile(SOURCE_DIR + CONFIG_FILE):
        print "ERROR: Unable to find config file"
        sys.exit(1)

    PARSER.read(SOURCE_DIR + CONFIG_FILE)

    dct = dict()
    dct['ignore_files'] = PARSER.get('menu', 'ignore_files').split(",")
    dct['name'] = PARSER.get('config', 'name')
    dct['url'] = PARSER.get('config', 'url')
    dct['destination'] = PARSER.get('config', 'destination')
    dct['menu_order'] = PARSER.get('menu', 'menu_order')

    if dct['menu_order']:
        # TODO: build a for loop for multiple ordered menu
        dct[dct['menu_order']] = PARSER.get('menu', dct['menu_order'])

    return dct


def get_page_info(filename, level):
    """ Get the page config
        :param filename: the filename
        :param level: the level
    """

    PARSER.read(filename)

    item = dict()
    item['title'] = PARSER.get('info', 'title')
    item['desc'] = PARSER.get('info', 'description')

    if level == 1:
        item['nb'] = get_nb_child(os.path.dirname(filename))

    elif level == 2 or level == 3:

        if PARSER.has_option('info', 'created_date'):
            item['created_date'] = date_time_format(
                PARSER.get('info', 'created_date'))

        if PARSER.has_option('info', 'author'):
            item['author'] = PARSER.get('info', 'author')

    return item


def get_template(filename):
    """ Get an HTML template
        :param filename: the filename
    """

    with codecs.open(filename, "r", "utf8") as my_file:
        tpl = my_file.read()

    return tpl


def get_breadcrumbs(folder):
    """ Get the page breadcrumbs
        :param folder: the folder name
    """

    folder2 = ""
    folder3 = ""
    folder = folder.replace(SOURCE_DIR, "").split("/")
    length = len(folder) - 1

    if length > 2:
        folder2 = folder[0]
        folder3 = folder[1]

    if DEBUG:
        print "(get_breadcrumbs) folder: "
        print folder
        print "(get_breadcrumbs) l: " + str(length)
        print "(get_breadcrumbs) folder2: " + folder2
        print "(get_breadcrumbs) folder3: " + folder3

    tpl = get_template(TEMPLATE_BREADCRUMB)
    template = Template(tpl)
    content = template.render(
        ROOT_TITLE=SITENAME,
        FOLDER2=folder2,
        FOLDER3=folder3
    )
    return content


def get_type(folder):
    """ Get the type of the page
        :param folder: the folder name
    """

    is_root = folder.replace(SOURCE_DIR, "") == ""

    if is_root:
        return TYPE_ROOT

    if has_child(folder):
        return TYPE_LIST

    return TYPE_PAGE


def has_child(folder):
    """ Current page has child?
        :param folder: the folder name
    """
    return get_nb_child(folder) > 0


def get_nb_child(folder):
    """ Get the number of child for a page
        :param folder: the folder name
    """
    lst = next(os.walk(folder))[1]
    return len(lst)


def get_page_content(fld, page_type):
    """ Get the page content
        :param fld: the folder name
        :param page_type: the page type
            isHomePage: If this is the home page, Nothing needed, load the page
            hasChild: If this page has sub pages, show a list
            Page: Show the page, Load _page.html and parse variables
    """

    folder = fld + ("" if fld[-1:] == "/" else "/")
    file_info = folder + PAGE_FILE
    filename = folder + PAGE_INDEX
    level = len(folder.replace(SOURCE_DIR, "").split("/")) - 1
    if DEBUG:
        print "(get_page_content) file_info : " + file_info
        print "(get_page_content) filename : " + filename
        print "(get_page_content) level : " + str(level)

    content = ""

    if page_type == TYPE_ROOT:
        with codecs.open(filename, "r", "utf8") as file_read:
            content = file_read.read()

    elif page_type == TYPE_LIST:

        # check what type we have
        # level 1 (list categories) or level 2 (list articles)
        # kinda cheesy but ...
        if level == 1:
            tpl = get_template(TEMPLATE_LIST_CATEGORY)
        elif level == 2:
            tpl = get_template(TEMPLATE_LIST_ARTICLE)
        else:
            return ""

        items = []

        list_items = next(os.walk(folder))[1]
        list_items = sorted(list_items)
        for list_item in list_items:
            fld = folder + list_item + "/" + PAGE_FILE
            url = "/" + (folder + list_item).replace(SOURCE_DIR, "") + "/"

            if DEBUG:
                print "(get_page_content) url: " + url
                print "(get_page_content) fld: " + fld

            item = get_page_info(fld, level)

            # get nb of items
            item['url'] = url

            items.append(item)

        # Get page info
        page = get_page_info(file_info, 9)

        template = Template(tpl)
        content = template.render(
            PAGE_TITLE=page['title'],
            records=items
        )

    else:

        if level == 1:
            tpl = get_template(TEMPLATE_PAGE)
        elif level == 3:
            tpl = get_template(TEMPLATE_PAGE_ARTICLE)
        else:
            return ""

        page = get_page_info(file_info, level)
        page_content = get_template(filename)
        template = Template(tpl)

        if level == 1:
            content = template.render(
                PAGE_TITLE=page['title'],
                CONTENT=page_content
            )

        elif level == 3:
            content = template.render(
                PAGE_TITLE=page['title'],
                BREADCRUMBS=get_breadcrumbs(folder),
                CREATED_DATE=page['created_date'],
                AUTHOR=page['author'],
                CONTENT=page_content
            )

    return content


def date_time_format(value, style='%A %B %d, %Y'):
    """ Get a human readable date format
         :param value: the date time
         :param style: the style / format
    """
    return datetime.datetime.fromtimestamp(
        int(value)).strftime(style)


def set_menu():
    """ Build the main menu
    """

    dct = collections.OrderedDict()

    for folder, subs, files in os.walk(SOURCE_DIR):

        subs.sort()
        files.sort()

        fld = folder.replace(SOURCE_DIR, "")
        splitted = fld.split("/")

        if len(splitted) >= 3:
            continue

        if len(splitted[0]) == 0:
            continue

        if splitted[0] in IGNORE_FILES:
            continue

        name = get_page_info(folder + "/" + PAGE_FILE, 0)['title']

        if len(splitted) == 1:

            dct[fld] = collections.OrderedDict()
            dct[fld]['name'] = name

        elif len(splitted) == 2:

            if 'child' not in dct[splitted[0]]:
                dct[splitted[0]]['child'] = collections.OrderedDict()

            # We are skipping now the "force menu"
            # so we can build it later
            if splitted[0] != MENU_ORDER:
                dct[splitted[0]]['child'][splitted[1]] = name

    # Build the force menu
    # TODO: Multiple force menu
    if MENU_ORDER:

        folder = SOURCE_DIR + MENU_ORDER + "/"
        items = CONFIG[MENU_ORDER].split(',')

        for item in items:
            page = folder + item + "/" + PAGE_FILE
            name = get_page_info(page, 9)['title']
            dct[MENU_ORDER]['child'][item] = name

    return dct


def get_menu(folder):
    """ Get the main menu
        :param folder: the folder name
    """
    folder1 = ""
    folder2 = ""
    fld = folder.split("/")

    if len(fld) == 1:
        folder1 = fld[0]
    elif len(fld) == 2 or len(fld) == 3:
        folder1 = fld[0]
        folder2 = fld[1]

    tpl = get_template(TEMPLATE_MENU)
    template = Template(tpl)
    content = template.render(
        MAIN_MENU=MENU,
        FOLDER1=folder1,
        FOLDER2=folder2
    )

    return content


def generate_sitemap(urls):
    """ Generate the sitemap
        :param urls: The urls
    """

    tpl = get_template(TEMPLATE_SITEMAP)
    template = Template(tpl)

    content = template.render(
        URLS=urls
    )

    save_file = HTML_DIR + SITEMAP_FILE

    if DEBUG:
        print "Saving: " + save_file
    else:
        print ".",

    with codecs.open(save_file, "w", "utf8") as file_save:
        file_save.write(content)


#
# Constants
#
PAGE_FILE = "page.ini"
PAGE_INDEX = "index.html"
CONFIG_FILE = "config.ini"
SITEMAP_FILE = "sitemap.xml"

TYPE_ROOT = "root"
TYPE_LIST = "list"
TYPE_PAGE = "page"

ROOT_DIR = sys.argv[1] + ("" if sys.argv[1][-1:] == "/" else "/")
SOURCE_DIR = ROOT_DIR + "source/"

# Config
CONFIG = get_config_info()
SITENAME = CONFIG['name']
SITEURL = CONFIG['url']
HTML_DIR = CONFIG['destination']
IGNORE_FILES = CONFIG['ignore_files']
MENU_ORDER = CONFIG['menu_order']

if not os.path.isdir:
    print "Destination directory does not exists"
    sys.exit(1)

# Templates config
TEMPLATE = SOURCE_DIR + "_template.html"
TEMPLATE_LIST_CATEGORY = SOURCE_DIR + "_list_category.html"
TEMPLATE_LIST_ARTICLE = SOURCE_DIR + "_list_article.html"
TEMPLATE_PAGE = SOURCE_DIR + "_page.html"
TEMPLATE_PAGE_ARTICLE = SOURCE_DIR + "_page_article.html"
TEMPLATE_BREADCRUMB = SOURCE_DIR + "_breadcrumb.html"
TEMPLATE_MENU = SOURCE_DIR + "_menu.html"
TEMPLATE_SITEMAP = SOURCE_DIR + SITEMAP_FILE

# Get the main template
TEMPLATE_DATA = get_template(TEMPLATE)

# Set the main menu
MENU = set_menu()

if DEBUG:
    print "ROOT_DIR = " + ROOT_DIR
    print "SOURCE_DIR= " + SOURCE_DIR
    print "HTML_DIR = " + HTML_DIR
    print "TEMPLATE = " + TEMPLATE
    print "SITENAME = " + SITENAME
    print "SITEURL = " + SITEURL
