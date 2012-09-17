'''
    Classic Cinema Addon for XBMC
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Watch films from http://classiccinemaonline.com.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE.txt for more details.
'''
import re
from urlparse import urljoin
from urllib import urlencode
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from xbmcswift2 import Plugin, download_page
from resources.lib.getflashvideo import get_flashvideo_url


plugin = Plugin('Classic Cinema', 'plugin.video.classiccinema', __file__)


BASE_URL = 'http://www.classiccinemaonline.com'
def full_url(path):
    return urljoin(BASE_URL, path)


@plugin.route('/')
def show_browse_methods():
    '''Default view. Displays the different ways to browse the site.'''
    items = [
        {'label': 'Movies', 'path': plugin.url_for('show_movie_genres')},
        {'label': 'Silent Films', 'path': plugin.url_for('show_silent_genres')},
        {'label': 'Serials', 'path': plugin.url_for('show_serials')},
    ]
    return items


@plugin.route('/movies/', name='show_movie_genres',
              options={'path': 'index.php/movie-billboards'})
@plugin.route('/silents/', name='show_silent_genres',
              options={'path': 'index.php/silent-films-menu'})
@plugin.route('/serials/', name='show_serials',
              options={'path': 'index.php/serials'})
def show_genres(path):
    '''For movies and silent films, will display genres. For serials, will
    display serial names.'''
    src = download_page(full_url(path))
    html = BS(src, convertEntities=BS.HTML_ENTITIES)

    a_tags = html.findAll('a', {'class': 'category'})
    items = [{'label': a.string,
              'path': plugin.url_for('show_movies', url=full_url(a['href'])),
             } for a in a_tags]
    return plugin.add_items(items)


@plugin.route('/movies/<url>/')
def show_movies(url):
    '''Displays available movies for a given url.'''
    # Need to POST to url in order to get back all results and not be limited
    # to 10. Currently can hack using only the 'limit=0' querystring, other
    # params aren't needed.
    data = {'limit': '0'}
    src = download_page(url, urlencode(data))
    html = BS(src, convertEntities=BS.HTML_ENTITIES)

    trs = html.findAll('tr', {'class': lambda c: c in ['even', 'odd']})

    items = [{'label': tr.a.string,
              'path': plugin.url_for('show_movie', url=full_url(tr.a['href'])),
              'is_playable': True,
              'info': {'title': tr.a.string},
             } for tr in trs]
    return plugin.add_items(items)


@plugin.route('/watch/<url>/')
def show_movie(url):
    '''Show the video.'''
    src = download_page(url)
    url = get_flashvideo_url(src=src)
    plugin.log.info('Resolved url to %s' % url)
    return plugin.set_resolved_url(url)


if __name__ == '__main__':
    plugin.run()
