import requests, itertools, sys, re
from multiprocessing import Pool
from optparse import OptionParser

def run(parser):
    """
        kicks off the show
    """

    options = check_options(parser)
    options.base_url = get_base_url(options)
    urls = get_urls(options)

    mprint("Starting buster with base url " + options.base_url)

    if options.parallel > 1:
        p = Pool(options.parallel)
        p.map(make_request, add_ext(urls,options))
    else: 
        for url in add_ext(urls,options):
            make_request(url)


def add_ext(urls, options):
    """
        generator which yields urls
        appended with the appropriate extensions
    """ 
    ctr = 0
    while ctr < len(urls):
        for ext in options.extensions:
            output = urls[ctr] + '.' + ext
            yield output
        ctr += 1


def init_parser():
    """
        Adds appropriate options and returns parser object
    """
    parser = OptionParser("Usage: -t hostname -f dictionary")
    parser.add_option("-f","--file",\
            dest="filename",\
            help="the wordlist to be used")
    parser.add_option("-t","--hostname",\
            dest="target",\
            help="the site to bust")
    parser.add_option("-p","--port",\
            dest="port",\
            help="the port",\
            default=80)
    parser.add_option("-l","--parallel",\
            dest="parallel",\
            help="number of processes to spawn",\
            default=1,\
            type='int')
    parser.add_option("-e","--extension",\
            dest="extensions",\
            help="extension to append to the wordlist,\nformat is -e=php,js,html",\
            type='string',\
            default=["html","js","php","jpg"],\
            action='callback',\
            callback=parse_extensions)
    return parser

def parse_extensions(options, opt, value, parser):
    """
        callback to turn -e a,b,c into ['a','b','c'] for extensions
    """
    args = []
    if value:
        args = value.split(',')

    args = list(filter(lambda x: len(x) > 0, args))

    if len(args) > 0:
        setattr(parser.values, options.dest, args)


def check_options(parser):
    """
        Error checking, returns the appropriate options
    """
    (options, args) = parser.parse_args()

    if not options.filename:
        parser.error("Filename required for dictionary file")

    if not options.target:
        if len(args) == 0:
            parser.error("Target required")
        else:
            options.target=args[0]

    return options

def get_urls(options):
    """
        takes the options and returns of urls to test
    """
    try:
        filename = open(options.filename ,'r')
    except FileNotFoundError as e:
        pexit("File not found")

    urls = []
    for line in filename.readlines():
        line = line.replace("\n","")
        if len(line) > 0 and line[0] != "#":
            url = options.base_url + line
            urls.append(url)

    return urls

def get_base_url(options):
    """
      constructs the base uri to test
    """
    protocols = ["http://","https://"]

    # check if any protocols are currently in the target
    if any(map(lambda x: (x in options.target), protocols)):
        base_url = options.target
    else:
        base_url = "http://" + options.target


    # check if ports are in the target
    m = re.search(":[0-9]*", options.target)
    if m is None:
        base_url = base_url + ":" + str(options.port) 

    base_url = base_url + "/"

    return base_url


def mprint(text):
    sys.stdout.write(text)


def pprint(response, url):
    """
        pretty prints output
    """ 
    sys.stdout.write("%s %s\n" % (url, response.status_code))

def pexit(string):
    """
        Print string and exits
    """
    sys.stdout.write(string + "\n")
    exit()

def make_request(url): 
    """    
        Checks the url for existence
    """
    try:
        r = (True, requests.get(url))
    except Exception as e:
        r = (False, e)
    if r[0] and r[1].status_code != 404:
        pprint(r[1], url)
    return r

