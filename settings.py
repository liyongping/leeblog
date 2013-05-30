#-*-coding:utf-8-*-

import os.path

DEBUG = True
LISTEN_PORT = 8080

# db settting
if DEBUG:
    DB_CONNECT_STRING = 'mysql://root:123456@localhost:3306/app_leeblog?charset=utf8'
else:
    #import sae.const
    #sae.const.MYSQL_DB      # 数据库名
    #sae.const.MYSQL_USER    # 用户名
    #sae.const.MYSQL_PASS    # 密码
    #sae.const.MYSQL_HOST    # 主库域名（可读写）
    #sae.const.MYSQL_PORT    # 端口，类型为，请根据框架要求自行转换为int
    #sae.const.MYSQL_HOST_S  # 从库域名（只读）
    DB_CONNECT_STRING = 'mysql://root:123456@localhost:3306/app_leeblog?charset=utf8'
    #DB_CONNECT_STRING = 'mysql://'+sae.const.MYSQL_USER+':'+sae.const.MYSQL_PASS+'@'+sae.const.MYSQL_HOST+':'+sae.const.MYSQL_PORT+'/'+sae.const.MYSQL_DB+'?charset=utf8'
DB_ECHO = True
DB_ENCODING = 'utf-8'
POOL_RECYCLE=5

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

BASE_PATH = os.path.dirname(__file__)
# the address path which the file will be uploaded in
FILE_MANAGER_PATH = os.path.join(BASE_PATH, u"static/upload/")

# the app will use this template
CURRENT_TEMPLATE_NAME = "default"

ALLOWED_HOSTS = []
LANGUAGE_CODE = 'en-us'
