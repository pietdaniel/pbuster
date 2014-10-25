import requests, itertools, sys
from multiprocessing import Pool
from optparse import OptionParser

def run(parser):
    """
        kicks off the show
    """
    options = get_options(parser)

    urls = get_urls(options)

    if options.parallel > 1:
        p = Pool(options.parallel)
        p.map(make_request, urls)
    else: 
        for url in urls:
            make_request(url)

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


def get_options(parser):
    """
        Error checking, returns the appropriate options
    """
    (options, args) = parser.parse_args()
    options.mutli_test=False

    if not options.filename:
        parser.error("Filename required for dictionary file")

    if not options.target:
        if len(args) == 0:
            parser.error("Target required")
        else:
            options.mutli_test=True
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
        if len(line) > 0:
            url = "http://" + options.target + ":" + str(options.port) + "/" + line 
            urls.append(url)

    new_urls = []
    for ext in options.extensions:
        for url in urls:
            new_urls.append(url + "." + ext)
    urls = new_urls + urls

    return urls

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

