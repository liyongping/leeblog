#-*-coding:utf-8-*-

import datetime

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.engine import reflection
from sqlalchemy import Column, Integer, SmallInteger, String, Date, Time,\
    Text, DateTime, create_engine, func, Table
from sqlalchemy.ext.declarative import declarative_base
from settings import DB_CONNECT_STRING, DB_ENCODING, DB_ECHO, POOL_RECYCLE

engine = create_engine(DB_CONNECT_STRING, encoding=DB_ENCODING, echo=DB_ECHO)
# 为了解决mysql gone away尝试使用NullPool和设置POOL_RECYCLE为5s
#engine = create_engine(DB_CONNECT_STRING, encoding=DB_ENCODING, echo=DB_ECHO, pool_recycle=POOL_RECYCLE, poolclass=NullPool)

Base = declarative_base()

class Comment(Base):
    __tablename__ = 'comment'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    parent = Column(Integer(11), default=0)
    post_id = Column(Integer(11), default=0)
    karma = Column(Integer(11), default=0)
    user_id = Column(Integer(11), default=0)
    author = Column(String(32), default='')
    author_email = Column(String(100), default='')
    author_url = Column(String(256), default='')
    author_ip = Column(String(100), default='')
    date = Column(DateTime, default=func.now())
    content = Column(Text, default='')
    approved = Column(String(20), default='')
    agent = Column(String(255), default='')
    type = Column(String(20), default='')

class CommentMeta(Base):
    __tablename__ = 'commentmeta'
    
    meta_id = Column(Integer(11), primary_key=True, autoincrement=True)
    comment_id = Column(Integer(11), default=0, nullable=False)
    meta_key = Column(String(255), default='', nullable=False)
    meta_value = Column(Text, nullable=False)
    
class Post(Base):
    __tablename__ = 'post'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    # this post will be published in this 'parent' page
    parent = Column(Integer(11), default=0, nullable=False)
    author = Column(Integer(11), default=0)
    date = Column(DateTime, default=func.now())
    modified = Column(DateTime, default=func.now(), onupdate=datetime.datetime.now)
    title = Column(Text, default='', nullable=False)
    content = Column(Text, default='')
    excerpt = Column(Text, default='')
    status = Column(String(20), default='enabled')
    comment_status = Column(String(20), default='enabled')
    authorname = Column(String(32), default='')
    #password = Column(String(32), default='')
    guid = Column(String(255), default='')
    # type: page post
    type = Column(String(20), default='post')
    # when it's a page, it will be ordered by 'order'
    order = Column(Integer(11), default=0)
    # mime_type:
    mime_type = Column(String(20), default='')
    comment_count = Column(Integer(11), default=0)

class PostMeta(Base):
    __tablename__ = 'postmeta'
    
    meta_id = Column(Integer(11), primary_key=True, autoincrement=True)
    post_id = Column(Integer(11), default=0, nullable=False)
    meta_key = Column(String(255), default='', nullable=False)
    meta_value = Column(Text, nullable=False)

class Link(Base):
    __tablename__ = 'link'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    url = Column(String(255), default='', nullable=False)
    rss = Column(String(255), default='')
    name = Column(String(255), default='', nullable=False)
    image = Column(String(255), default='')
    target = Column(String(255), default='')
    description = Column(String(255), default='')
    notes = Column(String(255), default='')
    #visible: hide, show
    visible = Column(String(20), default='')
    rating = Column(Integer(11), default=0)
    updated = Column(DateTime, default=func.now(), onupdate=datetime.datetime.now)
    
class Term(Base):
    __tablename__ = 'term'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    parent = Column(Integer(11), default=0)
    # the name and slug are not unique, but it's unique for post_tag and category
    name = Column(String(200), default='')
    # slug: alias
    slug = Column(String(200), default='')
    # taxonomy: category, post_tag, post_format
    taxonomy = Column(String(32), default='')
    description = Column(Text, default='')
    count = Column(Integer(11), default=0)
    term_groub = Column(Integer(11), default=0)

class Term_Relationship(Base):
    __tablename__ = 'term_relationship'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    post_id = Column(Integer(11), default=0, nullable=False)
    term_id = Column(Integer(11), default=0, nullable=False)
    term_order = Column(Integer(11), default=0, nullable=False)

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    loginname = Column(String(32), unique=True, nullable=False)
    displayname = Column(String(32), unique=True, nullable=False)
    _password = Column('password', String(64), default='', nullable=False)
    email = Column(String(250), default='')
    url = Column(String(250), default='')
    registered = Column(DateTime(), default=func.now(), nullable=False)
    # status: enabled, disabled
    status = Column(String(10), default='disabled', nullable=False)
    priviledge = Column(Integer(11), default=0, server_default='0', nullable=False)
    activation_key = Column(String(250), default='')
    
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        import hashlib
        # encrypt the password with md5
        self._password = unicode(hashlib.md5(password).hexdigest(),'utf-8')

class UserMeta(Base):
    __tablename__ = 'usermeta'
    
    meta_id = Column(Integer(11), primary_key=True, autoincrement=True)
    user_id = Column(Integer(11), default=0, nullable=False)
    meta_key = Column(String(255), default='', nullable=False)
    meta_value = Column(Text, nullable=False)

class Options(Base):
    __tablename__ = 'options'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    key = Column(String(255), default='', nullable=False)
    value = Column(Text, nullable=False)
    # autoload: yes or no
    autoload = Column(String(20), default='yes', nullable=False) #server_default='yes', 

class StatTrace(Base):
    __tablename__ = 'stattrace'
    
    id = Column(Integer(11), primary_key=True, autoincrement=True)
    date = Column(Date(), default=func.now(), nullable=False)
    time = Column(Time(), default=func.now(), nullable=False)
    ip = Column(String(39), default='')
    urlrequested = Column(Text, default='')
    agent = Column(Text, default='')
    referrer = Column(Text, default='')
    os = Column(String(128), default='')
    browser = Column(String(128), default='')
    searchengine = Column(String(128), default='')
    spider = Column(String(128), default='')
    feed = Column(String(128), default='')
    nation = Column(String(16), default='')
    realpost = Column(Integer(2), default=1)

def InitTables():
    # delete all tables
    #Base.metadata.drop_all(engine)
    #create all tables
    #Base.metadata.create_all(engine)
    db = scoped_session(sessionmaker(bind=engine))
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    
    default_category = 1
    
    # determine if it needs to re-create the table.
    if 'user' not in tables:
        User.__table__.create(engine)
        user = User(loginname = 'admin',
                        displayname = 'admin',
                        password = '123456',
                        status = 'enabled',
                        priviledge=0,
                        email = 'test@example.com')
        db.add(user)
        db.commit()
    
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'usermeta' not in tables:
        UserMeta.__table__.create(engine)

    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'post' not in tables:
        Post.__table__.create(engine)
        post = Post(title=u'第一篇文章哦',
                        content=u'欢迎使用leeblog博客系统',
                        authorname='admin')
        db.add(post)
        db.commit()
    
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'postmeta' not in tables:
        PostMeta.__table__.create(engine)
    
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'comment' not in tables:
        Comment.__table__.create(engine)
    
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'commentmeta' not in tables:
        CommentMeta.__table__.create(engine)

    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'link' not in tables:
        Link.__table__.create(engine)
    
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'term' not in tables:
        Term.__table__.create(engine)
        term = Term(name=u'未分类',
                slug='uncategoried',
                taxonomy='category');
        db.add(term)
        db.commit()
        default_category = term.id
        
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'term_relationship' not in tables:
        Term_Relationship.__table__.create(engine)
    
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'options' not in tables:
        Options.__table__.create(engine)
        db.add_all([Options(key='blogname', value='Lee Blog'),
                Options(key='blogdescription', value=u'欢迎使用leeblog博客系统'),
                Options(key='users_can_register', value='0'),
                Options(key='admin_email', value='test@example.com'),
                Options(key='comments_notify', value='0'),
                Options(key='posts_per_rss', value='10'),
                Options(key='rss_use_excerpt', value='0'),
                # 缺省的文章是未分类
                Options(key='default_category', value=default_category),
                # 是否允许评论
                Options(key='users_can_comment', value='1'),
                # 每页最多显示多少条文章
                Options(key='posts_per_page', value='10'),
                Options(key='posts_per_recent_post', value='10'),
                Options(key='posts_per_recent_comment', value='10'),
                Options(key='mailserver_url', value='mail.example.com'),
                Options(key='mailserver_login', value='login@example.com'),
                Options(key='mailserver_pass', value='password'),
                Options(key='mailserver_port', value='110')])
        db.commit()
    tables = reflection.Inspector.from_engine(engine).get_table_names()
    if 'stattrace' not in tables:
        StatTrace.__table__.create(engine)

InitTables()

if __name__ == '__main__':
    #InitTables()
    pass