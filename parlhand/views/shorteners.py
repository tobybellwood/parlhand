#from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404,redirect
from parlhand import models

def unshorten(*args, **kwargs):
    mapper = kwargs.pop('mapper')
    ident = kwargs.pop('ident')
    maps = {
        'p':'parliamentarian',
        'y':'party',
        }
    url_name = maps[mapper]
    return redirect('parlhand:%s'%url_name,ident)
