#-*-coding:utf-8-*-

import tornado.web
from module.models import  User, Options, Post, Term
from settings import CURRENT_TEMPLATE_NAME

class BaseHandler(tornado.web.RequestHandler):
    option_dict = {}
    
    @property
    def db(self):
        return self.application.db

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