# Root domain URL for danbooru. Do not place a slash at the end.
domain = 'http://danbooru.donmai.us'

from urllib.request import *
from urllib.parse import *
import json
from io import StringIO
import os
import os.path as osp
import argparse

NO_MAX = 100000

parser = argparse.ArgumentParser( description='A script to automate downloading images on Danbooru' )
parser.add_argument( '--username', '-u', help='Your username on danbooru' )
parser.add_argument( '--api-key', '-k', help='Your API Key on danbooru (Can be found in your account profile)' )
parser.add_argument( '--download-directory', '-d', help='The directory in which downloaded photos will be placed' )
parser.add_argument( '--max-posts', '-m', default=NO_MAX, help='The script will not download more than this number of posts.' )
parser.add_argument( 'tag', nargs='+', help='One or more tags to search with' )
args = parser.parse_args()

# Global variables based on user input arguments
username = args.username
api_key = args.api_key
download_dir = args.download_directory
max_posts = args.max_posts
search_tags = args.tag

#=============================================================

class UrlBuilder:
    def __init__( self, operation ):
        self._params = {}
        self._operation = operation
        
        # These are needed for every operation
        self.addparam( 'user', username )
        self.addparam( 'api_key', api_key )
        
    def _formaturl( self, params ):
        return '{}/{}?{}'.format( domain, self._operation, params )
        
    def addparam( self, name, value ):
        self._params[name] = value
        
    def build( self ):
        encoded_params = urlencode( self._params )
        return urlopen( self._formaturl( encoded_params ) )

#=============================================================

class RequestPosts:
    def __init__( self, *tags ):
        self._page = 1
        self._limit = 100 # booru supports 100 max per request
        self._tags = list(tags)
        
    def nextpage( self ):
        self._page += 1
        
    def limit( self, limit ):
        self._limit = limit
        
    def execute( self ):
        print( 'Grabbing posts from page {}...'.format( self._page ) )
        url = UrlBuilder( 'posts.json' )
        url.addparam( 'page', self._page )
        url.addparam( 'limit', self._limit )
        url.addparam( 'tags', ' '.join( self._tags ) )
        io = StringIO( url.build().read().decode() )
        return json.load( io )

#=============================================================

class Downloader:
    def __init__( self, search_tags ):
        tags_dir = ' '.join( search_tags )
        self._dest_dir = osp.join( download_dir, tags_dir )
        
        if not osp.exists( self._dest_dir ):
            os.makedirs( self._dest_dir )
            
    def image( self, md5, ext ):
        self._filename = md5 + '.' + ext
        self._image_path = osp.join( self._dest_dir, self._filename )
        self._image_url = domain + '/data/' + self._filename
        
    def isdownloaded( self ):
        return osp.exists( self._image_path )
        
    def download( self ):
        if not self.isdownloaded():
            print( '+ Downloading ' + self._filename )
            
            try:
                urlretrieve( self._image_url, self._image_path )
            except:
                #print( '  > FAILED/CANCELED! Removing...' )
                if osp.exists( self._image_path ):
                    os.remove( self._image_path )
                raise
        else:
            print( '- Skipping ' + self._filename + ' (already exists)' )

#=============================================================

def request_posts( *tags ):
    request = RequestPosts( *tags )
    json = []
    while len( json ) < max_posts:
        new_json = request.execute()
        if not new_json:
            break
            
        json.extend( new_json[:max_posts - len(json)] )
        request.nextpage()
        
    print( '\nA total of {} posts found for downloading'.format( len(json) ) )
    print( '----------------------------------------------------' )
    
    downloader = Downloader( tags )
    for post in json:
        downloader.image( post['md5'], post['file_ext'] )
        yield downloader
        
    print( '----------------------------------------------------' )

#=============================================================

print( 'Searching with tags:', search_tags )
print( 'NOTICE: If there are a lot of search results, this will take a while...\n' )

try:
    for post in request_posts( *search_tags ):
        post.download()
except:
    print( '\nERROR: Downloading was canceled or failed, aborting script...' )