def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict()
    #redirect(URL('home','index'))
    #redirect(URL('plugin_wiki','page/home'))
    
def list_all_projects():
        redirect(URL('default','list_all_projects'))


def contact():
    return dict()
    
def link():
    return dict()
