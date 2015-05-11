# Root domain URL for danbooru. Do not place a slash at the end.
domain = 'http://danbooru.donmai.us'

from urllib.request import *
from urllib.parse import *
from urllib.error import *
import json
from io import StringIO
import os
import os.path as osp
import argparse
import math
from help_text import help_text, program_help

optional_args = (
    ('-u', '--username', {}),
    ('-k', '--api-key', {}),
    ('-d', '--download-directory', {'default': '.'}),
    ('-m', '--max-posts', {'default': 1000000})
)

parser = argparse.ArgumentParser(description=program_help)
parser.add_argument('tag', nargs='+', help=help_text['tag'])

# Process optional arguments
for short, long, other_args in optional_args:
    parser.add_argument(long, short, help=help_text[long[2:]], **other_args)

args = parser.parse_args()

# Global variables based on user input arguments
download_dir = osp.normpath(args.download_directory)
max_posts = int(args.max_posts)
search_tags = args.tag

debug = False

#=============================================================


class UrlBuilder:

    def __init__(self, operation):
        self._params = {}
        self._operation = operation

        # These are needed for every operation
        self.addparam('user', args.username)
        self.addparam('api_key', args.api_key)

    def _formaturl(self, params):
        return '{}/{}?{}'.format(domain, self._operation, params)

    def addparam(self, name, value):
        self._params[name] = value

    def build(self):
        encoded_params = urlencode(self._params)
        return urlopen(self._formaturl(encoded_params))

#=============================================================


class RequestPosts:

    def __init__(self, *tags):
        self._page = 1
        self._limit = 100  # booru supports 100 max per request
        self._tags = list(tags)

    def nextpage(self):
        self._page += 1

    def limit(self, limit):
        self._limit = limit

    def execute(self):
        print('Grabbing posts from page {}...'.format(self._page))
        url = UrlBuilder('posts.json')
        url.addparam('page', self._page)
        url.addparam('limit', self._limit)
        url.addparam('tags', ' '.join(self._tags))
        io = StringIO(url.build().read().decode())
        return json.load(io)

#=============================================================


class Downloader:

    def __init__(self, search_tags, max_posts):
        tags_dir = ' '.join(search_tags).replace(':', '-')
        self._raw_dir = osp.join(download_dir, "_raw")
        self._tag_dir = osp.join(download_dir, tags_dir)
        self._count = 1
        self._max = max_posts

        if not osp.exists(self._raw_dir):
            os.makedirs(self._raw_dir)
        if not osp.exists(self._tag_dir):
            os.makedirs(self._tag_dir)

    def image(self, md5, ext):
        self._filename = md5 + '.' + ext
        self._raw_image_path = osp.join(self._raw_dir, self._filename)
        self._tag_image_path = osp.join(self._tag_dir, self._filename)
        self._image_url = domain + '/data/' + self._filename

    def isdownloaded(self):
        return osp.exists(self._raw_image_path)

    def islinked(self):
        return osp.lexists(self._tag_image_path)

    def _getprefix(self):
        padding = int(math.log10(self._max)) + 1
        preformatted = '  {:>' + str(padding) + '}/{}> '
        return preformatted.format(self._count, self._max)

    def download(self):
        prefix = self._getprefix()
        self._count += 1

        if not self.isdownloaded():
            if debug:
                print(prefix + 'Downloading ' + self._filename)

            try:
                urlretrieve(self._image_url, self._raw_image_path)
            except:
                #print( '  > FAILED/CANCELED! Removing...' )
                if osp.exists(self._raw_image_path):
                    os.remove(self._raw_image_path)
                raise
        else:
            if debug:
                print(prefix + 'Skipping download: ' + self._filename + ' (already exists)')

        if not self.islinked():
            os.symlink(self._raw_image_path, self._tag_image_path)
        else:
            if debug :
                print(prefix + 'Skipping link: ' + self._filename + ' (already exists)')


#=============================================================

extension_map = {
    "jpeg": "jpg",
}

def request_posts(*tags):
    request = RequestPosts(*tags)
    json = []
    while len(json) < max_posts:
        new_json = request.execute()
        if not new_json:
            break

        json.extend(new_json[:max_posts - len(json)])
        request.nextpage()

    print('\nA total of {} posts found for downloading'.format(len(json)))
    print('----------------------------------------------------')

    downloader = Downloader(tags, len(json))
    for post in json:
        md5 = post.get('md5')
        file_ext = post.get('file_ext')
        if file_ext in extension_map:
            file_ext = extension_map[file_ext]

        if not md5 or not file_ext:
            continue

        downloader.image(md5, file_ext)
        yield downloader

    print('----------------------------------------------------')

#=============================================================

print('Searching with tags:', search_tags)
# print('NOTICE: If there are a lot of search results, this will take a while...\n')

try:
    for post in request_posts(*search_tags):
        try:
            post.download()
        except URLError as e:
            print('\nERROR: URL/HTTP error:', e.reason, post._image_url)
    print('\nDownloading of all images complete!')
except KeyboardInterrupt:
    print('\nScript cancelled. Goodbye!')
