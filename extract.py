import sys
import json
import textwrap
from parsers import get_meta
import hashlib
import difflib
from os.path import exists
from shutil import copyfile
import toml
import logging


def process_file(config, url):
    meta = get_meta.init_meta()
    fn = "%s_%s" % (get_meta.get_domain(url), hashlib.sha1(
        url.encode("utf-8")).hexdigest())
    logging.info("processing %s %s" % (url, fn))
    if exists("./test_data/downloads/%s.html" % fn):
        logging.info("using downloaded html")
        meta = get_meta.crawl_meta(
            url, "./test_data/downloads/%s" % fn, config, None, False, True, False)
    else:
        meta = get_meta.crawl_meta(
            url, "./pages/%s" % fn, config, None, False, False, False)

    meta["text"] = textwrap.shorten(
        meta["text"], width=150, placeholder="...")
    return meta, fn


def diff_file(meta, url, fn):
    with open("./test_data/downloads/%s.meta" % fn) as f:
        ref_meta = f.read().splitlines()
        differ = False
        for line in difflib.unified_diff(ref_meta, normalize(meta).splitlines(), fromfile='Reference', tofile='Current', lineterm='', n=1):
            print(line)
            differ = True

        if differ:
            print("FAILED %s %s" % (url, fn))
        else:
            print("OK %s %s" % (url, fn))


class LogDBHandler(logging.Handler):
    def __init__(self, verbose):
        logging.Handler.__init__(self)
        self.verbose = verbose

    def emit(self, record):
        if self.verbose:
            print("%s %s" % (record.levelname, record.msg))


def order_dict(dictionary):
    result = {}
    for k, v in sorted(dictionary.items()):
        if isinstance(v, dict):
            result[k] = order_dict(v)
        elif isinstance(v, list):
            result[k] = sorted(v)
        else:
            result[k] = v
    return result


def normalize(meta):
    return json.dumps(order_dict(meta), indent=4, sort_keys=True)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Parameters:")
        print("-extract <config_file> <link>  - extract an arbitrary link")
        print("-add     <config_file> <link>  - add link to test set")
        print("-test    <config_file>         - run all test cases")
    else:
        config = toml.load(sys.argv[2])
        logger = LogDBHandler(config['verbose'])
        logging.getLogger('').addHandler(logger)
        logging.getLogger('').setLevel(logging.INFO)

        if len(sys.argv) > 3:
            if sys.argv[1] == "-extract":
                meta, fn = process_file(config, sys.argv[3])
                print(normalize(meta))
                if exists("./test_data/downloads/%s.meta" % fn):
                    diff_file(meta, sys.argv[3], fn)

            elif sys.argv[1] == "-add":
                meta, fn = process_file(config, sys.argv[3])
                copyfile("./pages/%s.html" %
                         fn, "./test_data/downloads/%s.html" % fn)
                try:
                    copyfile("./pages/%s.txt" %
                             fn, "./test_data/downloads/%s.txt" % fn)
                except:
                    pass
                with open("./test_data/downloads/%s.meta" % fn, "w") as f:
                    f.write(normalize(meta))
                with open("./test_data/links.txt", "a") as f:
                    f.write(sys.argv[3] + "\n")

        elif sys.argv[1] == "-test":
            links = []
            with open('./test_data/links.txt') as f:
                links = f.read().splitlines()
                for i in range(0, len(links)):
                    meta, fn = process_file(config, links[i])
                    diff_file(meta, links[i], fn)
