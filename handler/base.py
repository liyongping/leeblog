#-*-coding:utf-8-*-

import datetime

import tornado.web
from module.models import  User, Options, Post, Term, StatTrace
from settings import CURRENT_TEMPLATE_NAME
from stat import GetSpider, GetBrowser, GetOS, GetSE, GetNation, GetURL, IsFeed, IsSkipedURL, IsPost

class BaseHandler(tornado.web.RequestHandler):
    option_dict = {}
    
    @property
    def db(self):
        return self.application.db
    
    def prepare(self):
        urlrequested = self.request.uri
        if IsSkipedURL(urlrequested):
            return None
        urlrequested = GetURL(urlrequested)
        date = datetime.date.today()
        dt = datetime.datetime.now()
        time = datetime.time(dt.hour,dt.minute,dt.second)
        ip = self.request.remote_ip
        headers = self.request.headers
        referrer = ''
        try:
            referrer = headers['Referer']
        except:
            pass
        agent = ''
        try:
            agent = headers['User-Agent']
        except:
            pass
        spider = GetSpider(agent) if len(agent) != 0 else ''
        os = GetOS(agent) if len(agent) != 0 else ''
        browser = GetBrowser(agent) if len(agent) != 0 else ''
        searchengine = GetSE(referrer) if len(referrer) != 0 else ''
        nation = GetNation(headers['Accept-Language'], ip)
        feed = "" #urlrequested if IsFeed(urlrequested) else ''
        realpost = 1 if IsPost(urlrequested) else 0
        
        st = StatTrace(date=date,
                       time=time,
                       ip=ip,
                       urlrequested=urlrequested,
                       agent=agent,
                       referrer=referrer,
                       os=os,
                       browser=browser,
                       searchengine=searchengine,
                       spider=spider,
                       feed=feed,
                       nation=nation,
                       realpost=realpost)
        self.db.add(st)
        self.db.commit()

    def on_finish(self):
        self.db.close()

    def get_current_user(self):
        username = self.get_secure_cookie("blogadmin_user")
        if not username: return None
        return self.db.query(User).filter_by(loginname=username).first()
    
    @property
    def options(self):
        if not self.option_dict:
            option_list = self.db.query(Options).all()
            self.option_dict = {option.key:option.value for option in option_list}
        return self.option_dict
    
    def update_options(self):
        option_list = self.db.query(Options).all()
        self.option_dict = {option.key:option.value for option in option_list}
    
    def get_error_html(self, status_code, **kwargs):
        # get all pages
        pagelist = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        # get all categorys
        categorys = self.db.query(Term).filter_by(taxonomy='category').order_by(Term.name).all()
        # get all tags
        tags = self.db.query(Term).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc())
        
        return self.render_string(CURRENT_TEMPLATE_NAME+'/404.html',
                                  setting=self.options,
                                  user=self.current_user,
                                  navlist = GetNavList(pagelist),
                                  categorylist = categorys,
                                  taglist = tags,
                                  recentlist = recents)
class Navigate:
    def __init__(self, nid, name, parent, have_child):
        self.nid = nid
        self.name = name
        self.parent = parent
        # implicate if it have a child page
        self.have_child = have_child

def GetNavList(pages):
    navlist = []
    for page in pages:
        have_child = False
        for sub in pages:
            if sub.parent == page.id:
                have_child = True
                break
        navlist.append(Navigate(page.id, page.title, page.parent, have_child))
    return navlist