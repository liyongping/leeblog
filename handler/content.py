#-*-coding:utf-8-*-

import json
import datetime

from tornado.web import HTTPError
from handler.base import BaseHandler, GetNavList
from module.models import Post, Term, Comment, Term_Relationship
from utility import AlchemyEncoder
from settings import CURRENT_TEMPLATE_NAME
from handler.stat import GetStatInfo, GetPostStatInfo
from rss.PyRSS2Gen import RSS2, RSSItem

class ContentHandler(BaseHandler):
    def get_error_html(self, status_code, **kwargs):
        return self.render_string(CURRENT_TEMPLATE_NAME+'/404.html',
                                  setting=self.options,
                                  user=self.current_user,
                                  navlist = GetNavList(self.GetPages()),
                                  categorylist = self.GetCategorys(),
                                  taglist = self.GetTags(),
                                  recentPostList = self.GetRecentPosts(),
                                  recentCommentList = self.GetRecentComments())
    def GetPages(self):
        # get all pages
        pagelist = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        return pagelist
    
    def GetCategorys(self):
        # get all categorys
        categorys = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='category').order_by(Term.name).all()
        return categorys
    
    def GetTags(self):
        # get all tags
        tags = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        return tags
    
    def GetTermsWithRelationship(self):
        # get all terms with relationship
        terms = self.db.query(Term, Term_Relationship.post_id).join(Term_Relationship,Term.id==Term_Relationship.term_id).all()
        return terms
        
    def GetRecentPosts(self):
        posts_per_recent_post = 5
        if self.options.has_key('posts_per_recent_post'):
            posts_per_recent_post = self.options['posts_per_recent_post']
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc()).limit(posts_per_recent_post)
        return recents
    
    def GetRecentComments(self):
        posts_per_recent_comment = 5
        if self.options.has_key('posts_per_recent_comment'):
            posts_per_recent_comment = self.options['posts_per_recent_comment']
        # get recent latest comments
        recentComments = self.db.query(Comment).filter_by(approved='yes').order_by(Comment.date.desc()).limit(posts_per_recent_comment)
        return recentComments

class MainHandler(ContentHandler):
    def get(self):
        currentPage = 1
        try:
            currentPage = int(self.request.arguments['p'][0])
        except:
            pass
        # get all posts
        posts = self.db.query(Post).filter_by(status='enabled', type='post')
        postAmount = posts.count()
        posts_per_page = int(self.options['posts_per_page'])
        pageAmount = postAmount/posts_per_page
        if postAmount%posts_per_page != 0 and postAmount!=0:
            pageAmount +=1
        # limit offset http://stackoverflow.com/questions/13258934/applying-limit-and-offset-to-all-queries-in-sqlalchemy
        postlist = posts.order_by(Post.date.desc()).offset((currentPage-1)*posts_per_page).limit(posts_per_page).all()
        
        self.render(CURRENT_TEMPLATE_NAME+"/index.html",
                    setting=self.options,
                    user=self.current_user,
                    article = None,
                    postlist = postlist,
                    navlist = GetNavList(self.GetPages()),
                    categorylist = self.GetCategorys(),
                    taglist = self.GetTags(),
                    recentPostList = self.GetRecentPosts(),
                    recentCommentList = self.GetRecentComments(),
                    relationlist = self.GetTermsWithRelationship(),
                    currentPage = currentPage,
                    pageList = range(1,pageAmount+1))

class CategoryListHandler(BaseHandler):
    def get(self):
        pass
    def post(self):
        categorys = self.db.query(Term).filter_by(taxonomy='category').order_by(Term.name).all()
        clist = json.dumps(categorys, cls=AlchemyEncoder).replace("</", "<\\/")
        self.write(clist)

class TagListHandler(BaseHandler):
    def get(self):
        tags = self.db.query(Term).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        clist = json.dumps(tags, cls=AlchemyEncoder).replace("</", "<\\/")
        self.write(clist)
    def post(self):
        pass
    
class CommentListByPostIdHandler(BaseHandler):
    def get(self):
        pass
    def post(self):
        try:
            pid = self.request.arguments['post_id'][0]
            comments = self.db.query(Comment).filter_by(post_id=int(pid)).order_by(Comment.date).all()
            jsons = json.dumps(comments, cls=AlchemyEncoder).replace("</", "<\\/")
            self.write(jsons)
        except:
            pass
class CommentAddHandler(BaseHandler):
    def get(self):
        pass
    def post(self):
        comment_post_id = self.request.arguments['comment_post_id'][0]
        parent = self.request.arguments['comment_parent_id'][0]
        author = self.request.arguments['author'][0]
        email = self.request.arguments['email'][0]
        url = ""
        try:
            url = self.request.arguments['url'][0]
        except:
            pass
        content = self.request.arguments['comment'][0]
        if len(comment_post_id)==0 or len(author)==0 or len(email)==0 or len(content)==0:
            self.write('')
            return None
        comment = Comment(parent=int(parent),
                          post_id=int(comment_post_id),
                          author=author,
                          author_email=email,
                          author_url=url,
                          content=content,
                          approved='yes',
                          karma=0,
                          author_ip=self.request.remote_ip)
        self.db.add(comment)
        self.db.commit()
        parentComment = self.db.query(Comment).get(int(parent))
        if comment.parent == 0:
            comment.karma = comment.id
        else:
            comment.karma = parentComment.karma
        self.db.commit()
        parent_post = self.db.query(Post).get(comment.post_id);
        parent_post.comment_count = parent_post.comment_count+1;
        self.db.commit()
        # if comment save successfully, it will return parent comment and current comment
        commentpair = [parentComment,comment]
        commentjson = json.dumps(commentpair, cls=AlchemyEncoder).replace("</", "<\\/")
        self.write(commentjson)

class PostByCategoryName(ContentHandler):
    def get(self, name=''):
        currentPage = 1
        try:
            currentPage = int(self.request.arguments['p'][0])
        except:
            pass
        # get all posts
        category = self.db.query(Term).filter_by(taxonomy='category', slug=name).first()
        posts = self.db.query(Post).join(Term_Relationship,Post.id==Term_Relationship.post_id).filter(Term_Relationship.term_id==category.id).filter(Post.type=='post')
        postAmount = posts.count()
        posts_per_page = int(self.options['posts_per_page'])
        pageAmount = postAmount/posts_per_page
        if postAmount%posts_per_page != 0 and postAmount!=0:
            pageAmount +=1
        # get post of the 'currentPage' page 
        postlist = posts.order_by(Post.date.desc()).offset((currentPage-1)*posts_per_page).limit(posts_per_page).all()

        self.render(CURRENT_TEMPLATE_NAME+"/index.html",
                    setting=self.options,
                    user=self.current_user,
                    article = None,
                    postlist = postlist,
                    navlist = GetNavList(self.GetPages()),
                    categorylist = self.GetCategorys(),
                    taglist = self.GetTags(),
                    recentPostList = self.GetRecentPosts(),
                    recentCommentList = self.GetRecentComments(),
                    relationlist = self.GetTermsWithRelationship(),
                    currentPage = currentPage,
                    pageList = range(1,pageAmount+1))
    def post(self):
        pass

class PostByTagName(ContentHandler):
    def get(self, name=''):
        currentPage = 1
        try:
            currentPage = int(self.request.arguments['p'][0])
        except:
            pass
        # get all posts
        tag = self.db.query(Term).filter_by(taxonomy='post_tag', slug=name).first()
        posts = self.db.query(Post).join(Term_Relationship,Post.id==Term_Relationship.post_id).filter(Term_Relationship.term_id==tag.id).filter(Post.type=='post')
        postAmount = posts.count()
        posts_per_page = int(self.options['posts_per_page'])
        pageAmount = postAmount/posts_per_page
        if postAmount%posts_per_page != 0 and postAmount!=0:
            pageAmount +=1
        # get post of the 'currentPage' page 
        postlist = posts.order_by(Post.date.desc()).offset((currentPage-1)*posts_per_page).limit(posts_per_page).all()
        
        self.render(CURRENT_TEMPLATE_NAME+"/index.html",
                    setting=self.options,
                    user=self.current_user,
                    article = None,
                    postlist = postlist,
                    navlist = GetNavList(self.GetPages()),
                    categorylist = self.GetCategorys(),
                    taglist = self.GetTags(),
                    recentPostList = self.GetRecentPosts(),
                    recentCommentList = self.GetRecentComments(),
                    relationlist = self.GetTermsWithRelationship(),
                    currentPage = currentPage,
                    pageList = range(1,pageAmount+1))
    def post(self):
        pass

class PostById(ContentHandler):
    def get(self, pid=0):
        # get post
        post = self.db.query(Post).get(pid)
        # cannot find the post by id
        if not post:
            raise HTTPError(404)
        
        #siteStat = GetStatInfo(self.db)
        #postStat = GetPostStatInfo(self.db, self.request.uri)
        
        self.render(CURRENT_TEMPLATE_NAME+"/post.html",
                    setting=self.options,
                    #stat=dict(siteStat, **postStat),
                    user=self.current_user,
                    article = post,
                    postlist = [],
                    navlist = GetNavList(self.GetPages()),
                    categorylist = self.GetCategorys(),
                    taglist = self.GetTags(),
                    recentPostList = self.GetRecentPosts(),
                    recentCommentList = self.GetRecentComments(),
                    relationlist = self.GetTermsWithRelationship())
    def post(self):
        pass

class PostByPageId(ContentHandler):
    def get(self, pid=0):
        # get the page content as the post content
        post = self.db.query(Post).get(pid)
        # cannot find the post by id
        if not post:
            raise HTTPError(404)
        
        self.render(CURRENT_TEMPLATE_NAME+"/page.html",
                    setting=self.options,
                    user=self.current_user,
                    article = post,
                    postlist = None,
                    navlist = GetNavList(self.GetPages()),
                    categorylist = self.GetCategorys(),
                    taglist = self.GetTags(),
                    recentPostList = self.GetRecentPosts(),
                    recentCommentList = self.GetRecentComments(),
                    relationlist = self.GetTermsWithRelationship())
    def post(self):
        pass

class FeedHandler(ContentHandler):
    def get(self):
        items = []
        for post in self.GetRecentPosts():
            item = RSSItem(title = post.title,
                           link = "http://"+self.request.host+"/post/id/"+str(post.id),
                           description = post.content,
                           pubDate = post.date)
            items.append(item)
        rss = RSS2(
            title = self.options['blogname'],
            link = "http://"+self.request.host,
            description = self.options['blogdescription'],
            lastBuildDate = datetime.datetime.now(),
            items = items)
        xmlresult = rss.to_xml('UTF-8')
        self.write(xmlresult)