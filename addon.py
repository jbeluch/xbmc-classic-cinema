#!/usr/bin/env python
from resources.lib.plugin import XBMCSwiftPlugin, download_page
from resources.lib.getflashvideo import get_flashvideo_url
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from urlparse import urljoin
import re
from urllib import urlencode
try:
    import json
except ImportError:
    import simplejson as json

BASE_URL = 'http://www.classiccinemaonline.com'
__plugin__ = 'Classic Cinema'
__plugin_id__ = 'plugin.video.classiccinema'

plugin = XBMCSwiftPlugin(__plugin__, __plugin_id__)
#plugin.settings(plugin_cache=False, http_cache=False)

def full_url(path):
    return urljoin(BASE_URL, path)

@plugin.route('/', default=True)
def show_browse_methods():
    items = [
        {'label': 'Movies', 'url': plugin.url_for('show_movie_genres')},
        {'label': 'Silent Films', 'url': plugin.url_for('show_silent_genres')},
        {'label': 'Serials', 'url': plugin.url_for('show_serials')},
    ]
    return plugin.add_items(items)

@plugin.route('/movies/', name='show_movie_genres', path='index.php/movie-billboards')
@plugin.route('/silents/', name='show_silent_genres', path='index.php/silent-films-menu')
@plugin.route('/serials/', name='show_serials', path='index.php/serials')
def show_genres(path):
    src = download_page(full_url(path))
    html = BS(src)

    a_tags = html.findAll('a', {'class': 'category'})
    items = [{'label': a.string,
              'url': plugin.url_for('show_movies', url=full_url(a['href'])),
             } for a in a_tags]
    return plugin.add_items(items)

@plugin.route('/movies/<url>/')
def show_movies(url):
    # Currently can hack with only this url param
    data = {'limit': '0'}
    src = download_page(url, urlencode(data))
    html = BS(src)

    trs = html.findAll('tr', {'class': lambda c: c in ['even', 'odd']})

    items = [{'label': tr.a.string,
              'url': plugin.url_for('show_movie', url=full_url(tr.a['href'])),
              'is_folder': False,
              'is_playable': True,
              'info': {'title': tr.a.string, },
             } for tr in trs]
    return plugin.add_items(items)

@plugin.route('/watch/<url>/')
def show_movie(url):
    src = download_page(url)
    url = get_flashvideo_url(src)
    return plugin.set_resolved_url(url)

if __name__ == '__main__':
    #plugin.route_url('/movies/')
    #plugin.run()
    #plugin.interactive()
    plugin.crawl()
