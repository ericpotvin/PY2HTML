""" Website Library
"""

from ConfigParser import SafeConfigParser
from datetime import date
from jinja2 import Template

import collections
import datetime
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

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

    #Get the page details
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

    print "Saving: " + save_file

    with open(save_file, 'w') as file_:
        file_.write(tpl)


def get_config_info():
    """ Get the config / settings for the website
    """
    PARSER.read(SOURCE_DIR + CONFIG_FILE)

    dct = dict()
    dct['ignore_files'] = PARSER.get('menu', 'ignore_files').split(",")
    dct['name'] = PARSER.get('config', 'name')
    dct['url'] = PARSER.get('config', 'url')

    return dct


def get_page_info(filename, level):
    """ Get the page config
    """

    PARSER.read(filename)

    item = dict()
    item['title'] = PARSER.get('info', 'title')
    item['desc'] = PARSER.get('info', 'description')

    if level == 1:
        item['nb'] = get_nb_child(os.path.dirname(filename))

    elif level == 2 or level == 3:

        if PARSER.has_option('info', 'created_date'):
            item['created_date'] = datetimeformat(
                PARSER.get('info', 'created_date'))

        if PARSER.has_option('info', 'author'):
            item['author'] = PARSER.get('info', 'author')

    return item


def get_template(filename):
    """ Get an HTML template
    """

    tpl = ""

    with open(filename, 'r') as myfile:
        tpl = myfile.read()

    return tpl


def get_breadcrumbs(folder):
    """ Get the page breadcrumbs
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
    """Get the type of the page
    """

    is_root = folder.replace(SOURCE_DIR, "") == ""

    if is_root:
        return TYPE_ROOT

    if has_child(folder):
        return TYPE_LIST

    return TYPE_PAGE


def has_child(folder):
    """ Current page has child?
    """
    return get_nb_child(folder) > 0


def get_nb_child(folder):
    """ Get the number of child for a page
    """
    lst = next(os.walk(folder))[1]
    return len(lst)


def get_page_content(folder, page_type):
    """ Get the page content
    isHomePage: If this is the home page
        Nothing needed, just load the page
    hasChild: If this page has sub pages, show a list
        Load _has_child.html and parse variables
    Page: Show the page
        Load _page.html and parse variables
    """

    folder = folder + ("" if folder[-1:] == "/" else "/")
    fileinfo = folder + PAGE_FILE
    filename = folder + PAGE_INDEX
    level = len(folder.replace(SOURCE_DIR, "").split("/")) - 1
    if DEBUG:
        print "(get_page_content) fileinfo : " + fileinfo
        print "(get_page_content) filename : " + filename
        print "(get_page_content) level : " + str(level)

    content = ""

    if page_type == TYPE_ROOT:
        with open(filename) as file_read:
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
        page = get_page_info(fileinfo, 9)

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

        page = get_page_info(fileinfo, level)
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


def datetimeformat(value, style='%A %B %d, %Y'):
    """ Get a human readable date format
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
        splited = fld.split("/")

        if len(splited) >= 3:
            continue

        if len(splited[0]) == 0:
            continue

        if splited[0] in IGNORE_FILES:
            continue

        name = get_page_info(folder + "/" + PAGE_FILE, 0)['title']

        if len(splited) == 1:
            dct[fld] = collections.OrderedDict()
            dct[fld]['name'] = name

        elif len(splited) == 2:
            if 'child' not in dct[splited[0]]:
                dct[splited[0]]['child'] = collections.OrderedDict()

            dct[splited[0]]['child'][splited[1]] = name

    return dct


def get_menu(folder):
    """ Get the main menu
    """
    folder1 = ""
    folder2 = ""
    fld = folder.split("/")

    if len(fld) == 1:
        folder1 = fld[0]
    elif len(fld) == 2:
        folder1 = fld[0]
        folder2 = fld[1]

    print "folder = " + folder

    tpl = get_template(TEMPLATE_MENU)
    template = Template(tpl)
    content = template.render(
        MAIN_MENU=MENU,
        FOLDER1=folder1,
        FOLDER2=folder2
    )

    return content


#
# Constants
#

PAGE_FILE = "page.ini"
CONFIG_FILE = "config.ini"
TEMPLATE = "tpl.html"
PAGE_INDEX = "index.html"

TYPE_ROOT = "root"
TYPE_LIST = "list"
TYPE_PAGE = "page"

ROOT_DIR = sys.argv[1] + ("" if sys.argv[1][-1:] == "/" else "/")
SOURCE_DIR = ROOT_DIR + "source/"
HTML_DIR = sys.argv[1] + "public_html_test/"

TEMPLATE = SOURCE_DIR + "_template.html"
TEMPLATE_LIST_CATEGORY = SOURCE_DIR + "_list_category.html"
TEMPLATE_LIST_ARTICLE = SOURCE_DIR + "_list_article.html"
TEMPLATE_PAGE = SOURCE_DIR + "_page.html"
TEMPLATE_PAGE_ARTICLE = SOURCE_DIR + "_page_article.html"
TEMPLATE_BREADCRUMB = SOURCE_DIR + "_breadcrumb.html"
TEMPLATE_MENU = SOURCE_DIR + "_menu.html"

# Config
CONFIG = get_config_info()
SITENAME = CONFIG['name']
SITEURL = CONFIG['url']
IGNORE_FILES = CONFIG['ignore_files']

MENU = set_menu()

# Get the main template
TEMPLATE_DATA = get_template(TEMPLATE)

if DEBUG:
    print "ROOT_DIR = " + ROOT_DIR
    print "SOURCE_DIR= " + SOURCE_DIR
    print "HTML_DIR = " + HTML_DIR
    print "TEMPLATE = " + TEMPLATE
    print "SITENAME = " + SITENAME
    print "SITEURL = " + SITEURL
