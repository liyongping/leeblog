#-*-coding:utf-8-*-

'''
    refer to StatPress Visitors 1.5.4 (http://wordpress.org/extend/plugins/statpress-visitors/)
'''

import re
import os
import urlparse
import datetime

from sqlalchemy import func, distinct
from module.models import StatTrace

spiderList = []
browserList = []
osList = []
seList = []
langMap = {}
def InitStatDef():
    browserpath =  os.path.join(os.path.dirname(__file__), 'def\\browser.dat').replace('\\','/')
    feedpath =  os.path.join(os.path.dirname(__file__), 'def\\feed.dat').replace('\\','/')
    languagespath =  os.path.join(os.path.dirname(__file__), 'def\\languages.dat').replace('\\','/')
    ospath =  os.path.join(os.path.dirname(__file__), 'def\\os.dat').replace('\\','/')
    sepath =  os.path.join(os.path.dirname(__file__), 'def\\searchengine.dat').replace('\\','/')
    spiderpath =  os.path.join(os.path.dirname(__file__), 'def\\spider.dat').replace('\\','/')
    f = open(browserpath,'r')
    try:
        global browserList
        browserList = f.readlines()
    finally:
        f.close()
    
    f = open(spiderpath,'r')
    try:
        global spiderList
        spiderList = f.readlines()[:]
    finally:
        f.close()

    f = open(ospath,'r')
    try:
        global osList
        osList = f.readlines()[:]
    finally:
        f.close()

    f = open(sepath,'r')
    try:
        global seList
        seList = f.readlines()[:]
    finally:
        f.close()

    f = open(languagespath,'r')
    try:
        global langMap
        for line in f.readlines():
            value = line.split('|')
            if len(value[0]) == 0 or len(value[1]) == 0:
                continue
            langMap[value[1]] = value[0]
    finally:
        f.close()

InitStatDef()

def GetStatInfo(db):
    '''
    since: the start time of visiting
    totalvisitors: the visitor count of site except spider and feed
    totalpageviews: the view count of site except spider and feed
    todayvisitors: today, the visitor count of site except spider and feed
    todaypageviews: today, the view count of site except spider and feed
    '''
    stat  = {}
    
    #st = db.query(StatTrace).filter(StatTrace.ip != '').order_by(StatTrace.date.desc()).first()
    #stat['since'] = st.date
    stat['totalvisitors']  = db.query(func.count(distinct(StatTrace.ip))).filter_by(spider='', feed='').scalar()
    #stat['totalpageviews'] = db.query(func.count('*')).select_from(StatTrace).filter_by(spider='', feed='').scalar()
    # comment the today stat
    #stat['todayvisitors'] = db.query(func.count(distinct(StatTrace.ip))).filter_by(spider='', feed='', date=datetime.date.today()).scalar()
    #stat['todaypageviews'] = db.query(func.count(StatTrace.ip)).filter_by(spider='', feed='', date=datetime.date.today()).scalar()
    
    return stat;

def GetPostStatInfo(db, url):
    '''
    thistotalvisitors: the totalvisitors of the current post url
    thistodayvisitors: the todayvisitors of the current post url
    thistotalpageviews: the totalpageviews of the current post url
    thistodaypageviews: the todaypageviews of the current post url
    '''
    stat  = {}
    # comment the today stat
    stat['thistotalvisitors'] = db.query(func.count(distinct(StatTrace.ip))).filter_by(spider='', feed='', urlrequested=url).scalar()
    #stat['thistodayvisitors'] = db.query(func.count(distinct(StatTrace.ip))).filter_by(spider='', feed='', urlrequested=url, date=datetime.date.today()).scalar()
    
    #stat['thistotalpageviews'] = db.query(func.count('*')).select_from(StatTrace).filter_by(spider='', feed='', urlrequested=url).scalar()
    #stat['thistodaypageviews'] = db.query(func.count(StatTrace.ip)).filter_by(spider='', feed='', urlrequested=url, date=datetime.date.today()).scalar()
    return stat

def GetSpider(agent):
    agent = agent.replace(' ' ,'')
    for item in spiderList:
        value = item.split('|')
        if len(value[0]) == 0 or len(value[1]) == 0:
            continue
        if agent.find(value[1]) != -1:
            return value[0]
    return ""

def GetBrowser(agent):
    agent = agent.replace(' ' ,'')
    for item in browserList:
        value = item.split('|')
        if len(value[0]) == 0 or len(value[1]) == 0:
            continue
        if agent.find(value[1]) != -1:
            return value[0]
    return ""

def GetOS(agent):
    agent = agent.replace(' ' ,'')
    for item in osList:
        value = item.split('|')
        if len(value[0]) == 0 or len(value[1]) == 0:
            continue
        if agent.find(value[1]) != -1:
            return value[0]
    return ""

def GetSE(referrer):
    for item in seList:
        value = item.split('|')
        if len(value[0]) == 0 or len(value[1]) == 0:
            continue
        if referrer.find(value[1]) == -1:
            continue
        result=urlparse.urlparse(referrer)
        parametermap = urlparse.parse_qs(result.query,True)
        for k in parametermap.keys():
            if k == value[2]:
                return value[0]
    return ""

def GetNation(accept_Language, ip):
    try:
        if accept_Language:
            return accept_Language[0:2]
    except:
        pass
    return ""

def GetURL(uri):
    # home page with page id
    if uri[0:2] == '/?':
        return ''
    # home
    if uri == '/':
        return ''
    return uri

def IsFeed(urlRequested):
    return False

def IsPost(urlRequested):
    if urlRequested.find("/post/id/") != -1:
        return True
    return False

def IsSkipedURL(urlRequested):
    '''
    check if it needs to skip these urls:
        static file
        admin request
        ajax
    '''
    if re.search(r'.ico$', urlRequested):
        return True
    if re.search(r'favicon.ico', urlRequested):
        return True
    if re.search(r'.css$', urlRequested):
        return True
    if re.search(r'.js$', urlRequested):
        return True
    
    if urlRequested.find("/admin/") != -1:
        return True
    if urlRequested.find("/comment/add") != -1:
        return True
    if urlRequested.find("/comment/list") != -1:
        return True
    if urlRequested.find("/tag/list") != -1:
        return True
    if urlRequested.find("/category/list") != -1:
        return True
    
    return False


def unittest():
    print IsSkipedURL('/admin/page/edit/10')
    print IsSkipedURL('/category/list')
    print IsSkipedURL('/static/img/favour.ico')
    print IsSkipedURL('/admin/page/edit/10')
    print not IsSkipedURL('/post/id/6')
    print not IsSkipedURL('/post/category/python/?p=1')
    
    print not IsPost('/post/category/python/?p=1')
    print IsPost('/post/id/10')
    
    print 'spider:',GetSpider('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0')
    print 'brower:',GetBrowser('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0')
    print 'os:',GetOS('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0')
    print 'se:',GetSE('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0')
    
    from sqlalchemy.orm import scoped_session, sessionmaker
    from module.models import engine
    db = scoped_session(sessionmaker(bind=engine))
    print GetStatInfo(db)
    
if __name__ == '__main__':
    unittest()