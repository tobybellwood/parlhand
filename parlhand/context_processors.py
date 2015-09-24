from feincms.module.page.models import Page
from parlhand import models

def menu_handler(request):
    """
    FienCMS hates giving navigation to other pages, and we aren't forking 100 projects to add some decorators
    So this means the rest of the project gets a menu.
    """
    
    parl_menu = {}
    parl_menu['parliament'] = models.Parliament.objects.order_by('-number').first()
    parl_menu['ministry'] = models.Ministry.objects.order_by('-number').first() 

    page,created = Page.objects.get_or_create(override_url='/',
        defaults ={
            'title':'Default Home',
            'in_navigation':True,
            'featured':False
            })
    if created:
        print "I've auto assembled a home page for you, but this needs to be fixed!"
    return {
        'base_nav':page,
        'parl_menu':parl_menu,
        }