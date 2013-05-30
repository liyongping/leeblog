#-*-coding:utf-8-*-

import json
import os, datetime, types
import StringIO
from PIL import Image

from settings import BASE_PATH, FILE_MANAGER_PATH, STATIC_URL, STORAGE_DOMAIN_NAME
import sae.storage

#encode_json = cjson.encode
encode_json = json.dumps

path_exists = os.path.exists
normalize_path = os.path.normpath
absolute_path = os.path.abspath
split_path = os.path.split
split_ext = os.path.splitext

fileicons_path = STATIC_URL+'filemanager/images/fileicons/'

# 'http://localhost:8080/stor-stub/upload/'
storage = sae.storage.Client()
domain_path = storage.url(STORAGE_DOMAIN_NAME, '')

def put_obj2storage(file_name = '', data = '', expires='365', content_type=None, encoding= None, domain_name = STORAGE_DOMAIN_NAME):
    ob = sae.storage.Object(data = data, cache_control='access plus %s day' % expires, content_type=content_type, content_encoding= encoding)
    return storage.put(domain_name, file_name, ob)

class CkFinder(object):
    def __init__(self):
        pass

    def dirlist(self, request):
        result =['<ul class="jqueryFileTree" style="display: none;">']
        print 'storage.list(STORAGE_DOMAIN_NAME)',storage.list(STORAGE_DOMAIN_NAME)
        try:
            for f_item in storage.list(STORAGE_DOMAIN_NAME):
                file_name = f_item['name']
                print f_item
                ext = os.path.splitext(file_name)[1][1:]
                full_path = storage.url(STORAGE_DOMAIN_NAME, file_name)
                result.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (ext, full_path, file_name))
            result.append('</ul>')
        except:
            pass

        return ''.join(result)

    def rename(self, old, new):
        result = {}
        error_message = new
        success_code = "0"
        try:
            path = split_path(old)
            old_name = path[-1]
            new_name = new
            old_object = storage.get(STORAGE_DOMAIN_NAME, old_name)
            new_path = storage.put(STORAGE_DOMAIN_NAME, new_name, old_object)
            storage.delete(STORAGE_DOMAIN_NAME, old_name)
        except:
            success_code = "500"
            error_message = "There was an error renaming the file."
        finally:
            result = {
                        "Old Path" : '/',
                        "Old Name" : old_name,
                        "New Path" : '/',
                        "New Name" : new_name,
                        "Error" : error_message,
                        "Code" : success_code
                    }
        return encode_json(result)


    def delete(self, path):
        result = {}
        try:
            dir_path, name = split_path(path)
            storage.delete(STORAGE_DOMAIN_NAME, name)
            error_message = name + ' was deleted successfully.'
            success_code = "0"
        except:
            success_code = "500"
            error_message = "There was an error deleting the file. <br/> The operation was either not permitted or it may hav    e already been deleted."
        finally:
            result = {
                        "Path" : '/',
                        "Name" : name,
                        "Error" : error_message,
                        "Code" : success_code
                    }
        return encode_json(result)
        
    def addfolder(self, path, name):
        result = {}
        return encode_json(result)

    def upload(self, path, files):
        file_name = files[0]["filename"]
        file_url = put_obj2storage(file_name, files[0]["body"])
        result = {
                    "Name" : file_name,
                    "Path" : file_url,
                    "Code" : "0",
                    "Error" : ""
                }
        return '<textarea>' + encode_json(result) + '</textarea>'

    def get_dir_file(self, path):
        """
        SAE don't need param 'path', for it can get the path from 'STORAGE_DOMAIN_NAME'
        """
        result = {}
        dir_list = storage.list(STORAGE_DOMAIN_NAME)
        for o in dir_list:
            info = self.get_info(o['name'])
            result[o['name']] = info
        return result

    def get_info(self, request_path):
        request_file = split_path(request_path)[-1]
        path = storage.url(STORAGE_DOMAIN_NAME, request_file)
        imagetypes = ['.gif','.jpg','.jpeg','.png']
        ext = split_ext(path)
        preview = fileicons_path + ext[1][1:] + '.png'
        thefile = {"Path" : path,
                    "Filename" : split_path(path)[-1],
                    "File Type" : split_path(path)[1][1:],
                    "Preview" : preview,
                    "Properties" : {"Date Created" : '',
                                    "Date Modified" : '',
                                    "Width" : '',
                                    "Height" : '',
                                    "Size" : ''},
                    "Return" : path,
                    "Error" : '',
                    "Code" : 0 }
        if ext[1] in imagetypes:
            try:
                xx = storage.get(STORAGE_DOMAIN_NAME, request_file)
                
                file_object = StringIO.StringIO(xx.data)
                img = Image.open(file_object)
                xsize, ysize = img.size
                thefile["Properties"]["Width"] = xsize
                thefile["Properties"]["Height"] = ysize
                thefile["Preview"] = path
            except Exception,e:
                preview = fileicons_path + ext[1][1:] + '.png'
                thefile["Preview"] = preview

        thefile["File Type"] = os.path.splitext(path)[1][1:]
        file_stat = storage.stat(STORAGE_DOMAIN_NAME, request_file)
        create_time = datetime.datetime.fromtimestamp(file_stat['datetime']).isoformat(' ')
        thefile["Properties"]["Date Created"] = create_time
        thefile["Properties"]["Date Modified"] = create_time
        thefile["Properties"]["Size"] = file_stat['length']
        
        return thefile
