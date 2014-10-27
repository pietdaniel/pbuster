# pbuster
### A simple CLI directory brute forcer

Usage: ./bust -t hostname -f dictionary

```
Options:
  -h, --help            show this help message and exit
  -f FILENAME, --file=FILENAME
                        the wordlist to be used
  -t TARGET, --hostname=TARGET
                        the site to bust
  -p PORT, --port=PORT  the port
  -l PARALLEL, --parallel=PARALLEL
                        number of processes to spawn
  -e EXTENSIONS, --extension=EXTENSIONS
                        extension to append to the wordlist, format is
                        -e=php,js,html
```

TODO:
  -rate limiting

Usage: -t hostname -f dictionary
