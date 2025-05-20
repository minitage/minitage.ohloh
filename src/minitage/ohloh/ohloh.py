# Copyright (C) 2009, Makina Corpus <freesoftware@makina-corpus.com>
# -*- coding: utf-8 -*-
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.



__docformat__ = 'restructuredtext en'

from optparse import OptionParser
import ConfigParser
import os
import sys
import urllib
import urllib2
import hashlib
import elementtree.ElementTree as ET
import lxml
from lxml.html import fromstring as S
from lxml.etree import fromstring as X

from zope.testbrowser import browser


URL = 'http://www.ohloh.net'
PROJECT_ID='minitage'
MINITAGE_URL = 'http://git.minitage.org/git/'
FF2_USERAGENT =  'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'



def print_contents(browser, dest='~/.browser.html'):
    """Print the browser contents somewhere for you to see its context
    in doctest pdb, type print_contents(browser) and that's it, open firefox
    with file://~/browser.html."""
    open(os.path.expanduser(dest), 'w').write(browser.contents)


def get_minitage_repos():
    xml = S(read_url(MINITAGE_URL))
    repos = ['http://git.minitage.org/git/%s'%s
             for s in xml.xpath(
                 "//td[@class='sublevel-repo']/a/text()"
             )]
    return repos

def uniquify(r):
    tmp = []
    noecho = [tmp.append(e) 
              for e in r if 
              not e in tmp]
    return tmp

def get_config(cfg):
    config = ConfigParser.ConfigParser()
    config.read([cfg])
    return config._sections['config']

def open_url(url, params = None):
    if params:
        url = '%s?%s' % (url, params)
    return urllib2.urlopen(url)

def read_url(url, params = None):
    o = open_url(url, params)
    return o.read()

class Browser(browser.Browser):

    def __init__(self, url=None, mech_browser=None):
        browser.Browser.__init__(self, url, mech_browser)
        self.mech_browser.set_handle_robots(False)
        self.mech_browser.addheaders = [('User-agent' , FF2_USERAGENT)]
        if url is not None:
            self.open(url)

class OhlohUtil:

    def __init__(self,
                 url = URL,
                 project_id = PROJECT_ID,
                 email='',
                 password='',
                 api_key='',
                 oauth=''):
        self.url = url
        self.project_id = project_id
        self.email = email
        self.password = password
        self.api_key = api_key
        self.oauth = oauth
        self.browser = None

    def make_request(self,
                     service=None,
                     query = None,
                     params = None,
                     complete_url = None,
                     *args,
                     **kwargs
                    ):
        if not params : params = {}
        url = self.url
        if service:
            url += '/%s' % service
        else:
            url += '/projects/%s' % self.project_id
        if query:
            url += '/%s' % query
        if complete_url:
            url = complete_url

        base_params = {'api_key': self.api_key}
        base_params.update(params)
        url_params = urllib.urlencode(base_params)
        return read_url(url, url_params)

    def get_existing_repos(self):
        content = self.make_request(query='enlistments.xml')
        xml = X(content)
        repos = xml.xpath('//enlistment//url/text()')
        return repos

    def get_browser(self, fresh=False):
        if not self.browser or fresh:
            self.browser = Browser()

        self.browser.open(URL + '/sessions/new')
        self.browser.getControl(name='login[login]').value = self.email
        self.browser.getControl(name='login[password]').value = self.password
        self.browser.getControl(' Log In').click()
        return self.browser
    
    def add_repo(self, url, type='git'):
        mtype = {
            'git': 'GitRepository',
        }[type]
        br = self.get_browser()
        eurl = '%s/p/%s/enlistments/new' % (
            self.url, 
            self.project_id
        )
        br.open(eurl)
        br.getControl(name='repository[type]').value = [mtype]
        br.getControl(name='repository[url]').value = url
        br.getControl(name='commit').click()

def register_repo():
    parser = OptionParser()
    parser.add_option("-c", "--cfg", dest="config", default="config.cfg",) 
    (options, args) = parser.parse_args()
    c = get_config(options.config)
    ou = OhlohUtil(email=c['email'], password=c['password'],
                   api_key=c['api_key'], oauth=c['oauth'])
    new_repos = uniquify(get_minitage_repos())
    repos = ou.get_existing_repos()
    for repo in new_repos:
        if not repo in repos:
            print "add repo: %s" % repo
            ou.add_repo(repo)
        else:
            print "%s already registred, skipping" % repo

# vim:set et sts=4 ts=4 tw=80:
