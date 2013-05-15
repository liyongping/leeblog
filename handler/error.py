#-*-coding:utf-8-*-

from tornado.web import HTTPError
from handler.base import BaseHandler, GetNavList
from module.models import Post, Term, Comment, Term_Relationship
from settings import CURRENT_TEMPLATE_NAME

class NotFoundHandler(BaseHandler):
    def get(self):
        # cannot find
        raise HTTPError(404)
    def post(self):
        pass