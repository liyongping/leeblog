#-*-coding:utf-8-*-

import hashlib

from tornado.web import authenticated
from handler.base import BaseHandler

from module.models import User, Post, Term, Term_Relationship, Options
from form.forms import AdminLoginForm, PageAddForm, TermAddForm, PostAddForm, UserEditForm

class AmdinLoginHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            form = AdminLoginForm(self)
            self.render("admin/login.html",loginform=form)
        else:
            return self.redirect('/admin/home')
    def post(self):
        form = AdminLoginForm(self)
        if form.validate():
            username = form.username.data
            password = unicode(hashlib.md5(form.password.data).hexdigest(),'utf-8');
            user = self.db.query(User).filter_by(loginname=username).first()
            if user and user.password == password:
                self.set_secure_cookie("blogadmin_user", user.loginname)
                return self.redirect('/admin/home')
            else:
                form.password.errors.append('Username or Password is wrong')
        return self.render("admin/login.html",loginform=form)

class AmdinLogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie("blogadmin_user")
        self.redirect("/")

class AmdinHomeHandler(BaseHandler):
    @authenticated
    def get(self):
        return self.render('admin/home.html')
    @authenticated
    def post(self):
        pass

class AmdinProfileHandler(BaseHandler):
    @authenticated
    def get(self):
        form = UserEditForm(self)
        admin = self.current_user
        form.displayname.process_data(admin.displayname)
        form.email.process_data(admin.email)
        return self.render('admin/profile.html', form=form, user=admin, success=None)
    @authenticated
    def post(self):
        form = UserEditForm(self)
        admin = self.current_user
        if form.validate():
            password = unicode(hashlib.md5(form.password0.data).hexdigest(),'utf-8');
            user = self.db.query(User).get(admin.id)
            if user and user.password == password:
                user.displayname = form.displayname.data
                user.email = form.email.data
                user.password = form.password1.data
                self.db.commit()
                return self.render('admin/profile.html', form=form, user=admin, success=user)
            else:
                form.password0.errors.append('The Old Password is wrong')
        form.displayname.process_data(admin.displayname)
        form.email.process_data(admin.email)
        return self.render('admin/profile.html', form=form, user=admin, success=None)

class AmdinSettingHandler(BaseHandler):
    @authenticated
    def get(self):
        return self.render('admin/setting.html', setting=self.options, success=None)
    @authenticated
    def post(self):
        try:
            blogname = self.request.arguments['blogname'][0]
            blogdescription = self.request.arguments['blogdescription'][0]
            users_can_register = self.request.arguments['users_can_register'][0]
            admin_email = self.request.arguments['admin_email'][0]
            comments_notify = self.request.arguments['comments_notify'][0]
            posts_per_rss = self.request.arguments['posts_per_rss'][0]
            rss_use_excerpt = self.request.arguments['rss_use_excerpt'][0]
            default_category = self.request.arguments['default_category'][0]
            users_can_comment = self.request.arguments['users_can_comment'][0]
            posts_per_page = self.request.arguments['posts_per_page'][0]
            self.db.add_all([Options(key='blogname', value=blogname),
                Options(key='blogdescription', value=blogdescription),
                Options(key='users_can_register', value=users_can_register),
                Options(key='admin_email', value=admin_email),
                Options(key='comments_notify', value=comments_notify),
                Options(key='posts_per_rss', value=posts_per_rss),
                Options(key='rss_use_excerpt', value=rss_use_excerpt),
                Options(key='default_category', value=default_category),
                Options(key='users_can_comment', value=users_can_comment),
                Options(key='posts_per_page', value=posts_per_page)])
            self.db.commit()
            self.update_options()
        except:
            return self.render('admin/setting.html', setting=self.options, success=None)
        return self.render('admin/setting.html', setting=self.options, success=self.options)

class AmdinPageListHandler(BaseHandler):
    @authenticated
    def get(self):
        form = PageAddForm(self)
        pages = self.db.query(Post).filter_by(type='page').all()
        return self.render('admin/page.html', form=form, pages=pages)
    @authenticated
    def post(self):
        pass

class AmdinPageAddHandler(BaseHandler):
    @authenticated
    def get(self):
        form = PageAddForm(self)
        form.parent.query = self.db.query(Post).filter_by(type='page', status='enabled',parent=0).order_by(Post.title)
        return self.render('admin/page_add.html', form=form)
    @authenticated
    def post(self):
        form = PageAddForm(self)
        form.parent.query = self.db.query(Post).filter_by(type='page', status='enabled',parent=0).order_by(Post.title)
        if form.validate():
            title = form.title.data
            desc = form.description.data
            parent = form.parent.data.id if form.parent.data else 0
            order = form.order.data if form.parent.data else 0
            page = Post(title=title, content=desc, parent=parent, type='page',
                        author=self.current_user.id, status='enabled',
                        authorname=self.current_user.displayname,
                        order=order,
                        comment_count=0)
            self.db.add(page)
            self.db.commit()
            return self.redirect('/admin/page/list')
        return self.render("admin/page_add.html",form=form)

class AmdinPageDeleteHandler(BaseHandler):
    @authenticated
    def get(self, pid):
        self.db.delete(self.db.query(Post).get(pid))
        return self.redirect('/admin/page/list')
    @authenticated
    def post(self, pid):
        pass

class AmdinPageEditHandler(BaseHandler):
    @authenticated
    def get(self, pid):
        form = PageAddForm(self)
        current = self.db.query(Post).get(pid)
        #form.parent.query = self.db.query(Page).filter(Page.status=='enabled',Page.parent==0,Page.id!=current.id).order_by(Page.title)
        form.title.process_data(current.title)
        form.description.process_data(current.content)
        form.order.process_data(current.order)
        form.parent.process_data(self.db.query(Post).get(current.parent))
        form.parent.query = self.db.query(Post).filter(Post.status=='enabled').filter(Post.parent==0).filter(Post.id!=current.id).filter(Post.type=='page').order_by(Post.title)
        return self.render('admin/page_edit.html', form=form, current=current)
    @authenticated
    def post(self, pid):
        form = PageAddForm(self)
        current = self.db.query(Post).get(pid)
        form.parent.query = self.db.query(Post).filter(Post.status=='enabled').filter(Post.parent==0).filter(Post.id!=current.id).filter(Post.type=='page').order_by(Post.title)
        if form.validate():
            current.title = form.title.data
            current.content = form.description.data
            current.parent = form.parent.data.id if form.parent.data else 0
            current.order = form.order.data
            self.db.commit()
            return self.redirect('/admin/page/list')
        return self.render("admin/page_edit.html",form=form, current=current)

class AmdinPostListHandler(BaseHandler):
    @authenticated
    def get(self):
        posts = self.db.query(Post).filter_by(status='enabled', type='post').order_by(Post.date.desc()).all()
        return self.render('admin/post.html', posts=posts)
    @authenticated
    def post(self):
        pass

class AmdinPostAddHandler(BaseHandler):
    @authenticated
    def get(self):
        form = PostAddForm(self)
        form.parent.query = self.db.query(Post).filter(Post.status=='enabled').filter(Post.type=='page').order_by(Post.title)
        return self.render('admin/post_add.html',form=form, setting=self.options)
    @authenticated
    def post(self):
        form = PostAddForm(self)
        form.parent.query = self.db.query(Post).filter(Post.status=='enabled').filter(Post.type=='page').order_by(Post.title)
        if form.validate():
            title = form.title.data
            content = form.content.data
            parent = form.parent.data.id if form.parent.data else 0
            new_tags =[]
            try:
                new_tags = self.request.arguments['new_tags'][0].split(',')
            except:
                pass
            post_categorys = self.request.arguments['post_category[]']
            post = Post(title=title, content=content, parent=parent, 
                        author=self.current_user.id, status='enabled', 
                        authorname=self.current_user.displayname,
                        type='post',
                        comment_count=0)
            self.db.add(post)
            self.db.commit()
            self.bind_tags(new_tags, post.id)
            self.bind_category(post_categorys, post.id)
            return self.redirect('/admin/post/list')
        return self.render("admin/post_add.html", form=form, setting=self.options)
    def bind_tags(self, tags, post_id):
        # skip null string
        tags = [c for c in tags if len(c) > 0]
        for term in tags:
            termid = 0
            termname = term.strip()
            termslug = termname.lower()
            # check if this tag exists.
            tmpc = self.db.query(Term).filter(Term.slug == termslug).filter(Term.taxonomy=='post_tag').first();
            if tmpc == None:
                # new a tag
                tag = Term(name=termname, slug=termslug, parent=0, taxonomy='post_tag', count=0)
                self.db.add(tag)
                self.db.commit()
                termid = tag.id
            else:
                termid = tmpc.id
            # bind tag with post
            tr = Term_Relationship(post_id=post_id, term_id=termid, term_order=0)
            self.db.add(tr)
            tag = self.db.query(Term).get(termid)
            tag.count = tag.count+1
            self.db.commit()
    def bind_category(self, categorys, post_id):
        if len(categorys) > 1:
            try:
                categorys.remove(self.options['default_category'])
            except:
                pass
        for c in categorys:
            # bind tag with post
            tr = Term_Relationship(post_id=post_id, term_id=int(c), term_order=0)
            self.db.add(tr)
            category = self.db.query(Term).get(int(c))
            category.count = category.count+1
            self.db.commit()

class AmdinPostDeleteHandler(BaseHandler):
    @authenticated
    def get(self, pid):
        self.db.delete(self.db.query(Post).get(pid))
        terms = self.db.query(Term).join(Term_Relationship,Term.id==Term_Relationship.term_id).filter(Term_Relationship.post_id==pid).all()
        for term in terms:
            term.count = term.count -1
        
        self.db.query(Term_Relationship).filter_by(post_id=pid).delete()
        self.db.commit()
        return self.redirect('/admin/post/list')
    @authenticated
    def post(self, pid):
        pass

class AmdinPostEditHandler(BaseHandler):
    @authenticated
    def get(self, pid):
        form = PostAddForm(self)
        current = self.db.query(Post).get(pid)
        current_terms = self.db.query(Term).join(Term_Relationship,Term.id==Term_Relationship.term_id).filter(Term_Relationship.post_id==pid).distinct().all()
        current_tags = [term.name for term in current_terms if term.taxonomy=='post_tag']
        current_tags_str = ",".join(current_tags)
        current_categorys = [str(term.id) for term in current_terms if term.taxonomy=='category']
        current_categorys_str = ",".join(current_categorys)
        form.title.process_data(current.title)
        form.content.process_data(current.content)
        form.parent.process_data(self.db.query(Post).get(current.parent))
        form.parent.query = self.db.query(Post).filter(Post.status=='enabled').filter(Post.type=='page').order_by(Post.title)
        return self.render('admin/post_edit.html', form=form, current=current, current_tags=current_tags_str, current_categorys=current_categorys_str, setting=self.options)
    @authenticated
    def post(self, pid):
        form = PostAddForm(self)
        current = self.db.query(Post).get(pid)
        current_terms = self.db.query(Term).join(Term_Relationship,Term.id==Term_Relationship.term_id).filter(Term_Relationship.post_id==pid).distinct().all()
        current_tags = [term.name for term in current_terms if term.taxonomy=='post_tag']
        current_tags_str = ",".join(current_tags)
        current_categorys = [str(term.id) for term in current_terms if term.taxonomy=='category']
        current_categorys_str = ",".join(current_categorys)
        form.parent.query = self.db.query(Post).filter(Post.status=='enabled').filter(Post.type=='page').order_by(Post.title)
        if form.validate():
            title = form.title.data
            content = form.content.data
            parent = form.parent.data.id if form.parent.data else 0
            new_tags =[]
            try:
                new_tags = self.request.arguments['new_tags'][0].split(',')
            except:
                pass
            post_categorys = self.request.arguments['post_category[]']
            # update the tags and categorys relationship
            self.bindHander_tags(new_tags, current.id, current_tags)
            self.bindHander_categorys(post_categorys, current.id, current_categorys)
            # update the current Post
            current.title = title
            current.content = content
            current.parent = parent
            current.author = self.current_user.id
            self.db.commit()
            return self.redirect('/admin/post/list')
        return self.render('admin/post_edit.html', form=form, current=current, current_tags=current_tags_str, current_categorys=current_categorys_str, setting=self.options)
    def bindHander_tags(self, tags, post_id, current_tags):
        current_tag_slugs = [c.strip().lower() for c in current_tags]
        new_tag_slugs = [c.strip().lower() for c in tags]
        # skip null string
        new_tag_slugs = [c for c in new_tag_slugs if len(c) > 0]
        new_set = set(new_tag_slugs);
        old_set = set(current_tag_slugs);
        diff_set = new_set ^ old_set;
        for tag in diff_set:
            if tag in old_set: # remove relationship
                term = self.db.query(Term).filter(Term.slug == tag).filter(Term.taxonomy=='post_tag').first();
                self.db.query(Term_Relationship).filter_by(post_id=post_id, term_id=term.id).delete()
                term.count = term.count-1
            else: # bind, or new and then bind
                # check if it exists.
                tmpc = self.db.query(Term).filter(Term.slug == tag).filter(Term.taxonomy=='post_tag').first();
                if tmpc == None: # new a tag
                    term_id = 0;
                    # find the term_id with it's name
                    index = new_tag_slugs.index(tag);
                    tag = Term(name=tags[index], slug=tag, parent=0, taxonomy='post_tag', count=0)
                    self.db.add(tag)
                    self.db.commit()
                    term_id = tag.id
                else:
                    term_id = tmpc.id
                # bind tag with post
                tr = Term_Relationship(post_id=post_id, term_id=term_id, term_order=0)
                self.db.add(tr)
                # add count
                ctag = self.db.query(Term).get(term_id)
                ctag.count = ctag.count+1
            self.db.commit()
    def bindHander_categorys(self, categorys, post_id, current_categorys):
        if len(categorys) > 1:
            try:
                categorys.remove(self.options['default_category'])
            except:
                pass
        old_categorys = [int(c) for c in current_categorys]
        new_categorys = [int(c) for c in categorys]
        oldc = set(old_categorys);
        newc = set(new_categorys);
        diffc = oldc ^ newc;
        for term_id in diffc:
            category = self.db.query(Term).get(term_id)
            if term_id in oldc:#remove relationship
                self.db.query(Term_Relationship).filter_by(post_id=post_id, term_id=term_id).delete()
                category.count = category.count-1
            else:
                # bind tag with post
                tr = Term_Relationship(post_id=post_id, term_id=term_id, term_order=0)
                self.db.add(tr)
                category.count = category.count+1
            self.db.commit()

class AmdinCategoryListHandler(BaseHandler):
    @authenticated
    def get(self):
        form = TermAddForm(self)
        form.parent.query = self.db.query(Term).filter_by(taxonomy='category',parent=0).order_by(Term.name)
        categorys = self.db.query(Term).filter_by(taxonomy='category').order_by(Term.name).all()
        return self.render('admin/category.html', form=form, categorys=categorys)
    @authenticated
    def post(self):
        pass

class AmdinCategoryAddHandler(BaseHandler):
    @authenticated
    def get(self):
        pass
    @authenticated
    def post(self):
        form = TermAddForm(self)
        form.parent.query = self.db.query(Term).filter_by(taxonomy='category',parent=0).order_by(Term.name)
        if form.validate():
            name = form.name.data
            desc = form.description.data
            parent = form.parent.data.id if form.parent.data else 0
            page = Term(name=name.strip(), slug=name.strip().lower(),description=desc, parent=parent, taxonomy='category', count=0)
            self.db.add(page)
            self.db.commit()
            return self.redirect('/admin/category/list')
        categorys = self.db.query(Term).filter_by(taxonomy='category').order_by(Term.name).all()
        return self.render("admin/category.html", form=form, categorys=categorys)
    
class AmdinCategoryQuickAddHandler(BaseHandler):
    @authenticated
    def get(self):
        pass
    @authenticated
    def post(self):
        name = self.request.arguments['name'][0]
        parents=self.request.arguments['parent'][0].split(",")
        if len(name)>0 and len(parents) == 1:
            tmpc = self.db.query(Term).filter(Term.slug == name.strip().lower()).filter(Term.taxonomy=='category').all();
            if len(tmpc) != 0:
                self.write("error")
                return None;
            parent = int(parents[0])
            is_allow_insert = False
            if parent == 0:
                is_allow_insert = True
            else:
                parent_term = self.db.query(Term).get(parent)
                # check if it already exist. and its parent is fist stage
                if parent_term and parent_term.parent == 0:
                    is_allow_insert = True
            if is_allow_insert:
                category = Term(name=name, slug=name.strip().lower(), parent=int(parent), taxonomy='category', count=0)
                self.db.add(category)
                self.db.commit()
        else:
            self.write("Name is null, Or it only have one parent category!")

class AmdinCategoryDeleteHandler(BaseHandler):
    @authenticated
    def get(self, cid):
        self.db.query(Term_Relationship).filter_by(term_id=cid).delete()
        self.db.delete(self.db.query(Term).get(cid))
        return self.redirect('/admin/category/list')
    @authenticated
    def post(self, cid):
        pass

class AmdinCategoryEditHandler(BaseHandler):
    @authenticated
    def get(self, cid):
        form = TermAddForm(self)
        current = self.db.query(Term).get(cid)
        form.parent.query = self.db.query(Term).filter(Term.taxonomy=='category').filter(Term.parent==0).filter(Term.id!=current.id).order_by(Term.name)
        form.name.process_data(current.name)
        form.description.process_data(current.description)
        form.parent.process_data(current.parent)
        return self.render('admin/category_edit.html', form=form, current=current)
    @authenticated
    def post(self, cid):
        form = TermAddForm(self)
        current = self.db.query(Term).get(cid)
        form.parent.query = self.db.query(Term).filter(Term.taxonomy=='category').filter(Term.parent==0).filter(Term.id!=current.id).order_by(Term.name)
        if form.validate():
            current.name = form.name.data.strip()
            current.slug = current.name.strip().lower()
            current.description = form.description.data
            current.parent = form.parent.data.id if form.parent.data else 0
            self.db.commit()
            return self.redirect('/admin/category/list')
        return self.render("admin/category_edit.html",form=form, current=current)