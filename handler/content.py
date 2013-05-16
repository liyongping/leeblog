#-*-coding:utf-8-*-

import json

from tornado.web import HTTPError
from handler.base import BaseHandler, GetNavList
from module.models import Post, Term, Comment, Term_Relationship
from utility import AlchemyEncoder
from settings import CURRENT_TEMPLATE_NAME


class MainHandler(BaseHandler):
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
        # get all pages
        pagelist = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        # get all categorys
        categorys = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='category').order_by(Term.name).all()
        # get all tags
        tags = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc())
        # get all terms with relationship
        terms = self.db.query(Term, Term_Relationship.post_id).join(Term_Relationship,Term.id==Term_Relationship.term_id).all()
        
        self.render(CURRENT_TEMPLATE_NAME+"/index.html",
                    setting=self.options,
                    user=self.current_user,
                    navlist = GetNavList(pagelist),
                    categorylist = categorys,
                    taglist = tags,
                    article = None,
                    postlist = postlist,
                    recentlist = recents,
                    relationlist = terms,
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
        # if comment save successfully, it will return parent comment and current comment
        commentpair = [parentComment,comment]
        commentjson = json.dumps(commentpair, cls=AlchemyEncoder).replace("</", "<\\/")
        self.write(commentjson)

class PostByCategoryName(BaseHandler):
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
        
        # get all pages
        pagelist = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        # get all categorys
        categorys = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='category').order_by(Term.name).all()
        # get all tags
        tags = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc())
        # get all terms with relationship
        terms = self.db.query(Term, Term_Relationship.post_id).join(Term_Relationship,Term.id==Term_Relationship.term_id).all()
        
        self.render(CURRENT_TEMPLATE_NAME+"/index.html",
                    setting=self.options,
                    user=self.current_user,
                    navlist = GetNavList(pagelist),
                    categorylist = categorys,
                    taglist = tags,
                    article = None,
                    postlist = postlist,
                    recentlist = recents,
                    relationlist = terms,
                    currentPage = currentPage,
                    pageList = range(1,pageAmount+1))
    def post(self):
        pass

class PostByTagName(BaseHandler):
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
        
        # get all pages
        pagelist = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        # get all categorys
        categorys = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='category').order_by(Term.name).all()
        # get all tags
        tags = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc())
        # get all terms with relationship
        terms = self.db.query(Term, Term_Relationship.post_id).join(Term_Relationship,Term.id==Term_Relationship.term_id).all()
        
        self.render(CURRENT_TEMPLATE_NAME+"/index.html",
                    setting=self.options,
                    user=self.current_user,
                    navlist = GetNavList(pagelist),
                    categorylist = categorys,
                    taglist = tags,
                    article = None,
                    postlist = postlist,
                    recentlist = recents,
                    relationlist = terms,
                    currentPage = currentPage,
                    pageList = range(1,pageAmount+1))
    def post(self):
        pass

class PostById(BaseHandler):
    def get(self, pid=0):
        # get all pages
        pagelist = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        # get all categorys
        categorys = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='category').order_by(Term.name).all()
        # get all tags
        tags = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        # get post
        post = self.db.query(Post).get(pid)
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc())
        # get all terms with relationship
        terms = self.db.query(Term, Term_Relationship.post_id).join(Term_Relationship,Term.id==Term_Relationship.term_id).filter(Term_Relationship.post_id==pid).all()
        # cannot find the post by id
        if not post:
            raise HTTPError(404)
        
        self.render(CURRENT_TEMPLATE_NAME+"/post.html",
                    setting=self.options,
                    user=self.current_user,
                    navlist = GetNavList(pagelist),
                    categorylist = categorys,
                    taglist = tags,
                    article = post,
                    postlist = [],
                    recentlist = recents,
                    relationlist = terms)
    def post(self):
        pass

class PostByPageId(BaseHandler):
    def get(self, pid=0):
        # get all pages
        pages = self.db.query(Post).filter_by(status='enabled', type='page').order_by(Post.order.desc()).all()
        # get all categorys
        categorys = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='category').order_by(Term.name).all()
        # get all tags
        tags = self.db.query(Term).filter(Term.count>0).filter_by(taxonomy='post_tag').order_by(Term.name).all()
        # get the page content as the post content
        post = self.db.query(Post).get(pid)
        # get recent latest posts
        recents = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc())
        # get all terms with relationship
        terms = self.db.query(Term, Term_Relationship.post_id).join(Term_Relationship,Term.id==Term_Relationship.term_id).all()
        
        # cannot find the post by id
        if not post:
            raise HTTPError(404)
        
        self.render(CURRENT_TEMPLATE_NAME+"/page.html",
                    setting=self.options,
                    user=self.current_user,
                    navlist = GetNavList(pages),
                    categorylist = categorys,
                    taglist = tags,
                    article = post,
                    postlist = None,
                    recentlist = recents,
                    relationlist = terms)
    def post(self):
        pass