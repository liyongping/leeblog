#-*-coding:utf-8-*-

import wtforms

class FormDataDict(dict):
    '''Tornado handler arguments to MultiDict, wtforms required.'''
    def __init__(self, arguments):
        self.arguments = arguments

    def __iter__(self):
        return iter(self.arguments)

    def __len__(self):
        return len(self.arguments)

    def __contains__(self, name):
        return (name in self.arguments)

    def getlist(self, key):
        """
        Returns the list of values for the passed key. If key doesn't exist,
        then an empty list is returned.
        """
        try:
            return [i.decode("utf-8") for i in self.arguments[key]]
        except KeyError:
            return []


class Form(wtforms.Form):
    '''Base form class'''
    def __init__(self, handler=None, obj=None, prefix='', formdata=None, **kwargs):
        if handler:
            formdata = FormDataDict(handler.request.arguments)
            self.handler = handler
            self.current_user = handler.current_user
        super(Form, self).__init__(formdata=formdata, **kwargs)