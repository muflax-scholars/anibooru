
# Your username on danbooru.
username = ''

# This is your API Key. You can get this in your profile on danbooru.
api_key = ''

# Root domain URL for danbooru. Do not place a slash at the end.
domain = 'http://danbooru.donmai.us'

download_dir = 'pics'

max_posts = 500

from urllib.request import *
from urllib.parse import *
import json
from io import StringIO
import os
import os.path as osp

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
                print( '  > FAILED/CANCELED! Removing...' )
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
        print( 'requesting' )
        new_json = request.execute()
        if not new_json:
            break
            
        json.extend( new_json[:max_posts - len(json)] )
        request.nextpage()
        
    print( 'A total of {} posts found for downloading'.format( len(json) ) )
    
    downloader = Downloader( tags )
    
    for post in json:
        downloader.image( post['md5'], post['file_ext'] )
        yield downloader

#=============================================================

try:
    for post in request_posts( 'shoes', 'fairy_tail' ):
        post.download()
except:
    print( ' ' )
    print( 'Downloading was canceled or failed, aborting script...' )