# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import mutex
global_mutex = mutex.mutex()

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    if 'profile' not in auth.settings.actions_disabled:
        auth.settings.actions_disabled.append('profile')
    if 'register' not in auth.settings.actions_disabled:
        auth.settings.actions_disabled.append('register')
    user_id = auth.user.email.split('@')[0]
    welcome_msg = "Welcome to the FFPL website Team %s!" % user_id
    response.flash = T(welcome_msg)
    import json, os
    with open(os.path.join(request.folder, 'static', 'teams.json')) as df:
        team = json.load(df)
    with open(os.path.join(request.folder, 'static', 'mapping.json')) as df:
        members = json.load(df)
    captains =[]
    for i in team[user_id]:
        captains.append(members[i])
    # TODO: Set gameweek from config
    import datetime, os, json
    from dateutil import tz
    import datetime
    with open(os.path.join(request.folder, 'private', 'deadlines.json')) as df:
        deadlines = json.load(df)
    dt = deadlines['GW11']
    deadline_time = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]), int(dt[6]), tzinfo=tz.gettz('Asia/Calcutta'))
    
    form_msg = 'Choose your captain for gameweek 10:'
    form = FORM(form_msg)
    form.append(BR())
    for i in captains:
        form.append(INPUT(_name='Captains', _type= 'radio',value=str(i), _value=str(i)))
        form.append(str(i))
        form.append(BR())
    form.append(INPUT(_type='submit'))
    form.append(BR())
    if form.accepts(request,session, keepvalues=True, onvalidation=validate_with_time):
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = form.errors
    return dict(message=T('Welcome to FFPL!'), form=form, deadline=str(deadline_time))


def validate_with_time(form):
    import datetime, os, json
    from dateutil import tz
    with open(os.path.join(request.folder, 'private', 'deadlines.json')) as df:
        deadlines = json.load(df)
    dt = deadlines['GW11'] #TODO: Update latest Gameweek
    deadline_time = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]), int(dt[6]), tzinfo=tz.gettz('Asia/Calcutta'))
    current_time = datetime.datetime.now(tz=tz.gettz('Asia/Calcutta'))
    if deadline_time < current_time:
        form.errors = 'You are too late. Fine shall be imposed.'
    else:
        with open(os.path.join(request.folder, 'static', 'reverse_mapping.json')) as df:
            members = json.load(df)
        with open(os.path.join(request.folder, 'private', 'captains_gameweek.json')) as df:
            captains = json.load(df)
        if 'GW11' in captains:
            captains['GW11'][auth.user.email.split('@')[0]] = members[str(form.vars.Captains)]
            global global_mutex
            global_mutex.lock(set_captain, json.dumps(captains))
        else:
            raise HTTP(404, 'Why the f*** are you trying to set a captain before we announced it? :P')

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    if 'profile' not in auth.settings.actions_disabled:
        auth.settings.actions_disabled.append('profile')
    if 'register' not in auth.settings.actions_disabled:
        auth.settings.actions_disabled.append('register')
    return dict(form=auth())

def set_captain(captains):
    import os
    fd = open(os.path.join(request.folder, 'private', 'captains_gameweek.json'), 'w+')
    fd.write(captains)
    global global_mutex
    global_mutex.unlock()

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
