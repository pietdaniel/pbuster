import requests, itertools, sys, re, select, os
from time import time
from multiprocessing import Pool
from optparse import OptionParser

def run(parser):
    """
        kicks off the show
    """
    t1 = time()

    options = check_options(parser)

    mprint("Starting buster with base url " + options.base_url + "\r\n")

    urls = get_urls(options)
    urls = url_gen(urls, options)


    if options.parallel > 1:
        p = Pool(options.parallel)
        p.map(make_request, urls)
    else: 
        for url in urls:
            make_request(url)

    mprint("Finished checking %d sites in %f seconds" % (options.count, (time() - t1)))
    mprint("\r\n")

def url_gen(urls, options):
    """
        generator which yields urls appended 
        with the appropriate extensions
    """ 
    ctr = 0
    t1=time()
    while ctr < len(urls):
        for ext in options.extensions:
            key_handler(ctr,t1)
            options.count += 1
            output = urls[ctr] + '.' + ext
            yield output
        ctr += 1

def key_handler(ctr,t1):
    """
        Prints status on keystroke
    """
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0] and not dont:
        mprint("\rTotal scanned %d in %f seconds" % (ctr, (time() - t1)))
        sys.stdin.readline()
        sys.stdin.flush()

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
        adds request count and base url options
    """
    (options, args) = parser.parse_args()

    if not options.filename:
        parser.error("Filename required for dictionary file")

    if not options.target:
        if len(args) == 0:
            parser.error("Target required")
        else:
            options.target=args[0]

    options.count = 0

    options.base_url = get_base_url(options)

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
    m = re.search(":[0-9]+", options.target)
    if m is None:
        base_url = base_url + ":" + str(options.port) 

    base_url = base_url + "/"

    return base_url


def mprint(text):
    sys.stdout.write(str(text))


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
        headers = {
          'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/32.0',
          'Accept':'*/*',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Connection':'keep-alive'
        }
        req = requests.get(url)
        r = (True, req)
    except Exception as e:
        r = (False, e)
    if r[0] and r[1].status_code != 404:
        pprint(r[1], url)
    return r

