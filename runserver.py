#-*-coding:utf-8-*-

import tornado.ioloop
import tornado.web
import tornado.httpserver
import wsgiref.simple_server
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import LISTEN_PORT, DEBUG
from module.models import engine
from app import urls, settings, WsgiApplication

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, urls, **settings)
        # Have one global connection to the blog DB across all handlers
        self.db = scoped_session(sessionmaker(bind=engine))

def main():
    #tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(LISTEN_PORT)
    tornado.ioloop.IOLoop.instance().start()

def wsgi_main():
    server = wsgiref.simple_server.make_server('', LISTEN_PORT, WsgiApplication())
    server.serve_forever()
    
if __name__ == "__main__":
    wsgi_main()
