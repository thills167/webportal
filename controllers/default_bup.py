# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

########################## Tips
#http://stackoverflow.com/questions/12354353/duplicate-a-record-and-its-references-in-web2py


#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    redirect(URL('default','list_all_projects'))
    #redirect(URL('plugin_wiki','page/home'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def authenticate(uid,pid,func):   
   result = db(db.role.user == uid)(db.role.approval_status==1)(db.role.project == pid).select(db.role.ALL)
   myroles = [role_list[int(k.role)] for k in result]
   is_coordinator = db(db.project.project_coordinator == uid).select(db.project.ALL)
   if func == 'roles':
	if len(is_coordinator):
	  error = ''
	else:
	   error = 'You must be a project co-ordinator to manage roles'
	return error  
   if func == 'add_project':
	if len(is_coordinator):
	  error = ''
	else:
	   error = ''
        return error
   if func == 'add_sample':
	if 'experimentalist' in myroles:
	  error = ''
	else:
	   error = 'SignUp for  "Experimentalist Role" in this project to add a sample. Use Browser back button to navigate to Project View.'
        return error
   if func == 'experimentalist':
	if 'experimentalist' in myroles:
	  error = ''
	else:
	   error = 'You must be an experimentalist to add the biosource information of a sample'
        return error
   if func == 'my_samples':
	if  'experimentalist' in myroles:
	  error = ''
	else:
	   error = 'You are not authorized to view this page'
        return error

def basic_groups(pid):
    """ creates the basic groups on general basis or id basis """
    if not pid:
        for i in role_list:
	   auth.add_group(i,i) 
    else:
        pid_groups = [str(pid)+'#'+i for i in role_list]
	for k in pid_groups:
	   auth.add_group(k,k)
    return locals()	   


@auth.requires_login()
def add_project():
    error = authenticate(auth.user.id,'','add_project')
    form = SQLFORM(db.project,fields=['name','code','start_date','project_description','project_literature_reference','project_journal_name'],showid=False)
    form.add_button('Back', URL('list_all_projects'))
    form.vars.project_coordinator = auth.user.id
    if form.process().accepted:
       response.flash ='accepted'
       result = db(db.project.name == form.vars.name).select(db.project.ALL).first()
       basic_groups(result.id)
       db.role.insert(user=auth.user.id,project=result.id,role=6,approval_status=1,member_since=now)
       redirect(URL('project_viewer',args = form.vars.id))
    elif form.errors:
       response.flash = 'errors'
    return locals()

@auth.requires_login()
def remove_project():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), [])
    ]
    """takes an id and removes the project """ 
    pid  = request.args(0)
    pid_groups = [str(pid)+'#'+i for i in role_list]
    for z in pid_groups:
	pgid = auth.id_group(z)
	auth.del_group(pgid)
    del db.project[pid]
    return locals()

def add_experiment():
    grid = SQLFORM.grid(db.experiment)
    return locals()

def new_affiliation():
    form = SQLFORM(db.affiliation)
    return locals()

def edit_project():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), []),
    (T('Project'), False, URL('default','project_viewer',args=request.args),[])
    ]
    crud.settings.update_next = URL('project_viewer',args=request.args)
    form=crud.update(db.project,request.args(0),deletable=False)
    return locals();
 
@auth.requires_login()
def project_viewer():
    pid = request.args[-1]
    project=db(db.project.id==pid).select(db.project.ALL).first()
    cord = db(db.auth_user.id==project.project_coordinator).select(db.auth_user.ALL).first()
    
    if authenticate(auth.user.id,'','roles') == '':
      response.menu = [
      (T('Home'), False, URL('default','list_all_projects'), []),
      (T('Project'), False, URL('default','project_viewer',args=request.args[-1]),[
      (T('Grant Role'),False,URL('roles',args=project.id)),
      (T('Edit Project'),False,URL('edit_project',args=project.id)),
      (T('SignUP'),False,URL('reg_project',args=project.id))]
      )
      ]
    else :
      response.menu = [
      (T('Home'), False, URL('default','list_all_projects'), []),
      (T('Project'), False, URL('default','project_viewer',args=request.args[-1]),[
      (T('SignUP'),False,URL('reg_project',args=project.id))]
      )
      ]
      
    if project.project_status == '1':
      response.menu+= [
      (T('Published Samples'), False,URL('list_all_pub_samples',args=(pid)),[])
      ]
    elif authenticate(auth.user.id,pid,'add_sample')=='':
        response.menu+= [
        (T('Samples'), False,URL('my_samples',args=(pid)),[
        (T('My Samples'), False,URL('my_samples',args=(pid))),
        ])
        ]
    if len(request.args) == 2:
        response.flash = 'Project Succesfully ' + request.args[-2]
       
    users=db(db.role.approval_status==1)(db.role.project==pid)(db.role.project == db.project.id)(db.role.user==db.auth_user.id).select(db.role.ALL,db.auth_user.ALL)
    is_coordinator = ''
    myroles = ''
    if auth.user:
      is_coordinator = db(db.project.id == pid)(db.project.project_coordinator == auth.user.id).select(db.project.ALL).first()
      result = db(db.role.user == auth.user.id)(db.role.project == pid).select(db.role.ALL)
      myroles = [role_list[int(k.role)] for k in result]
      
    return locals()


def add_sample():
  """ creates a exp on an project basis and should continue to fill the bio source data """
  """ available to the experimentalist """ 
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  if 'new' in request.args:
   pid = request.args[-3]
  else:
   pid = request.args(0)
  error = authenticate(auth.user.id,pid,'add_sample') 
  form = SQLFORM(db.sample,fields=['name','code','description','scientific_name'],showid=False)
#added a field project in sample table
#added two more fields in form insert root/replica etc and scientific name
  if form.validate():
      i = db.sample.insert(experimentalist=auth.user.id,name=form.vars.name,code=form.vars.code ,description=form.vars.description,experiment=pid,scientific_name=form.vars.scientific_name,working_status=1,publication_status=0)
      response.flash = 'sample has been created'
      redirect(URL('list_all_dev_projects',args=['project','sample.project',pid])) 
      # redirect to the sample creation 
  elif form.errors:
      response.flash = 'Form has errors'
  return locals()

def sample_viewer():
   response.menu = [
   (T('Home'), False, URL('default','list_all_projects'), [])
   ]
   i = request.args[-1]
   if 'view' in request.args: 
	form = SQLFORM(db.sample, i,readonly =True,showid=False)
   if 'edit' in request.args: 
	form = SQLFORM(db.sample, i,showid=False)
   if form.process().accepted:
	response.flash = 'form accepted'
	redirect(URL('list_all_dev_projects',args = request.args[0:-3])) 
   elif form.errors:
	response.flash = 'form has errors'
   return dict(form=form)

@auth.requires_login()
def list_all_projects():
    response.menu = [
    (T('Home'), False, URL('default','index'), [])
    #(T('Home'), False, URL('default','list_all_projects'), []),
    #(T('Project'), False, URL('default','list_all_projects'), [(T('Add Project'),False,URL('default','add_project'))])
    ]
    form=FORM(
              INPUT(_name='name', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    form.elements('input[type=submit]')[0]["_value"] = "Search"
    if form.accepts(request,session):
      redirect(URL('grid?keywords=tomato')) 
    
    #form=FORM('',INPUT(_name='name') ,INPUT(_type='submit'))
    #if form.process().accepted:
      #redirect(URL('grid')) 
    pub_projects = db(db.project.project_status == 1)(db.project.project_coordinator==db.auth_user.id).select(db.project.ALL,db.auth_user.ALL)
    dev_projects = db(db.project.project_status == 0)(db.project.project_coordinator==db.auth_user.id).select(db.project.ALL,db.auth_user.ALL)
    authenticated = 'no'
    if auth.user:
	if auth.user.position=='4':
	    authenticated = 'yes'
    return locals()

def grid():
  # query=((db.project.project_status==0)&(db.experiment.project==db.project.id)&(db.sample.experiment==db.experiment.id)&(db.biosource.sample_name==db.sample.id))
   query=((db.project.project_status==0)&(db.experiment.project==db.project.id)&(db.sample.experiment==db.experiment.id)&(db.sample.id==db.biosource.sample_name))
   #query=((db.project.project_status==0))
#   query=((db.sample.experiment==db.experiment.id)&((db.sample.id==db.biosource.sample_name)|(db.sample.id==db.plant_growth_condition.sample_name)))
   grid = SQLFORM.grid(query)
   return locals() 

def temp():
   q1 = (db.project.project_status ==  0)
   q2 = (db.sample.publication_status == True)
   ck = {}
   fi = [db.project.name,db.project.project_coordinator,db.project.start_date,db.project.project_status,db.experiment.code,db.sample.name,db.sample.code,db.biosource.sample_name,db.plant_growth_condition.sample_name,db.treatments.sample_name,db.harvests.sample_name,db.extraction_preparation.sample_name,db.gas_chromatography.sample_name,db.liquid_chromatography.sample_name,db.mass_spectroscopy.sample_name,db.raw_data_storage_information.sample_name]
   l1=[lambda row: A('View Post',_href=URL("default","view",args=[row.id]))]
   links={'project':l1}
   grid = SQLFORM.smartgrid(db.project,ck,fields=fi,links=links,linked_tables=['experiment','sample','biosource','plant_growth_condition','treatments','harvests','extraction_preparation','gas_chromatography','liquid_chromatography','mass_spectroscopy','raw_data_storage_information']) 
   return locals() 

def list_all_pub_projects():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), [])
    ]
    q1 = (db.project.project_status ==  1)
    q2 = (db.sample.publication_status == True)
    ck = {'project':q1,'sample':q2}
    fi = [db.project.name,db.project.project_coordinator,db.project.start_date,db.project.project_status,db.experiment.code,db.sample.name,db.sample.code,db.sample.replica,db.biosource.sample_name,db.plant_growth_condition.sample_name,db.treatments.sample_name,db.harvests.sample_name,db.extraction_preparation.sample_name,db.gas_chromatography.sample_name,db.liquid_chromatography.sample_name,db.mass_spectroscopy.sample_name,db.raw_data_storage_information.sample_name]
    if 'view' in request.args or 'edit' in request.args or 'new' in request.args:
    	router()
    grid = SQLFORM.smartgrid(db.project,ck,fields=fi,editable=False,deletable=False,create = False,linked_tables=['experiment','sample','biosource','plant_growth_condition','treatments','harvests','extraction_preparation','gas_chromatography','liquid_chromatography','mass_spectroscopy','raw_data_storage_information']) 
    
    return locals()

@auth.requires_login()
def list_all_dev_projects():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), [])
    ]
    db.sample.experimentalist.default=auth.user.id
    db.experiment.experimentalist.default=auth.user.id
    db.sample.experiment.writable = False
    db.sample.parent.readable = False
    db.sample.experiment.readable = False
    db.experiment.experimentalist.writable = False
    q1 = (db.project.project_status ==  0)
    q2 = (db.sample.experimentalist == auth.user.id)
    ck = {'project':q1,'sample':q2}
    fi = [db.project.name,db.project.project_coordinator,db.project.start_date,db.project.project_status,db.experiment.name,db.experiment.code,db.experiment.description,db.sample.name,db.sample.code,db.sample.publication_status,db.biosource.sample_name,db.plant_growth_condition.sample_name,db.treatments.sample_name,db.harvests.sample_name,db.extraction_preparation.sample_name,db.gas_chromatography.sample_name,db.liquid_chromatography.sample_name,db.mass_spectroscopy.sample_name,db.spectrophotometry.sample_name,db.raw_data_storage_information.sample_name]
    edit_dict = {'project':False}
    delete_dict = {'project':False}
#Allow only one original sample to be added in an experiment others are replicates
    addsample = True
   # if 'sample' in request.args and 'new' in request.args:
   #      count = db(db.sample.experiment==request.args[-3]).count()
   #      if(count>0):
   #        db.sample.replica.default = 'replicate'
   #       # db.sample.replica.requires=IS_IN_SET(['replicate','alicot'])
   #      else:
   #        db.sample.replica.default = 'Original'
   #        db.sample.replica.writable = False
           
    create_dict = {'project':False,'sample':addsample}
    orderby_dict ={'sample':db.sample.name} 
#Links for replicating samples  
    args= request.args[0:5]
    #args1=['project',request.args[1],request.args[2],request.args[3],request.args[4],"biosource.sample_name","edit","biosource"]
    l1=[lambda row: A('R+',_href=URL("default","duplicate",args=request.args[:]+["replicate"]+[row.id])), \
	      # lambda row: A('copy',_href=URL("default","replicate",args=request.args[:]+[row.id])),\
	       lambda row: A('A+',_href=URL("default","duplicate",args=request.args[:]+["aliqout"]+[row.id])), \
	       dict(header='BIO',body=lambda row: A(''+tes(row.id,'biosource'),_href=URL("default","router",args=getargs(row.id,args,"biosource")))), \
	       dict(header='PGC',body=lambda row: A(''+tes(row.id,'plant_growth_condition'),_href=URL("default","router",args=getargs(row.id,args,"plant_growth_condition")))), \
	       dict(header='Trt',body=lambda row: A(''+tes(row.id,'treatments'),_href=URL("default","router",args=getargs(row.id,args,"treatments")))), \
	       dict(header='Har',body=lambda row: A(''+tes(row.id,'harvests'),_href=URL("default","router",args=getargs(row.id,args,"harvests")))), \
	       dict(header='Ext',body=lambda row: A(''+tes(row.id,'extraction_preparation'),_href=URL("default","router",args=getargs(row.id,args,"extraction_preparation")))), \
	       dict(header='GC',body=lambda row: A(''+tes(row.id,'gas_chromatography'),_href=URL("default","router",args=getargs(row.id,args,"gas_chromatography")))), \
	       dict(header='LC',body=lambda row: A(''+tes(row.id,'liquid_chromatography'),_href=URL("default","router",args=getargs(row.id,args,"liquid_chromatography")))), \
	       dict(header='MS',body=lambda row: A(''+tes(row.id,'mass_spectroscopy'),_href=URL("default","router",args=getargs(row.id,args,"mass_spectroscopy")))), \
	       dict(header='SPM',body=lambda row: A(''+tes(row.id,'spectrophotometry'),_href=URL("default","router",args=getargs(row.id,args,"spectrophotometry")))),
               lambda row: A('Files',_href=URL('default','multiple_files',args=row.id))]
    links={'sample':l1}    
    
#customized Views for certain forms using router   
    if 'view' in request.args or 'edit' in request.args or 'new' in request.args:
     	router()
    s={'sample':lambda ids : redirect(URL('default', 'multiple', vars=dict(id=ids)))}
    
    grid = SQLFORM.smartgrid(db.project,ck,fields=fi,editable=edit_dict,orderby=orderby_dict,create=create_dict,deletable=delete_dict,links=links,linked_tables=['experiment','sample','raw_data_storage_information'],links_placement='right',showbuttontext=True,selectable = s) 
    return locals()
def multiple():
    s=request.vars['id']
    queries=[] 
    brows = db(db.biosource.id<0).select() 
    for i in s:
     queries.append(db.biosource.sample_name==i)
     brows = brows | db(db.biosource.id == i).select()
    query = reduce(lambda a,b:(a|b),queries)
    brows = db(query).select()
    return dict(brows=brows,query=query) 
#gets table name and rowid as input and creates another row with same details as rowid recod has
def tes(a,table):
    if db(db[table].sample_name==a).count()==0:
     return "Add"
    else:
        return "Edit"
    return "Add"
def getargs(a,args,table):
    row = db(db[table].sample_name==a).select(db[table].id).first()
    if row:
        args=args+[table+".sample_name",a,"edit",table,row.id]
        return args
    else:
        args = args+[table+".sample_name",a,"new",table]
        return args

def copy(sid):
    if db(db.template.user==auth.user.id).count() == 0:
       db.template.insert(user=auth.user.id, sample=sid)
    else:   
       db(db.template.user == auth.user.id).update(sample=sid)
    #redirect(URL('list_all_dev_projects',args=request.args[0:-1]))
    #Unique fields take care
    #product.update(sampleid='temp')
    return() 
def duplicate():
    if True:
        rec = db(db.sample.id==request.args[-1]).select(db.sample.ALL).first()
        rec.update(parent=rec.id,replica=str(request.args[-2]))
        for f in db.sample.fields:
	    if f != 'id':
		db.sample[f].default = rec[f]
	db.sample.replica.default = request.args[-2]
	db.sample.replica.writable = False
	db.sample.parent.readable = False
	rep_count =0; ali_count=0;
	rep_last= db(db.sample.parent==rec.id)(db.sample.replica=='replicate').select().last()
	if rep_last:
	    rep_count = int(rep_last.code.split('-')[1])
	ali_last= db(db.sample.parent==rec.id)(db.sample.replica=='aliqout').select().last()
	if ali_last:
	    ali_count = int(ali_last.code.split('-')[1])	    
	if request.args[-2] == 'replicate':
	    db.sample.code.default = rec.code + '_r-'+ str(rep_count+1)
	    db.sample.name.default = rec.name + '_r-'+ str(rep_count+1)
	if request.args[-2] == 'aliqout':
	    db.sample.code.default = rec.code + '_a-'+ str(ali_count+1)
	    db.sample.name.default = rec.name + '_a-'+ str(ali_count+1)
	db.sample.name.writable= False
	db.sample.code.writable= False	
        #in_row = db.sample.insert(**db.sample._filter_fields(rec))
	form = SQLFORM(db.sample)
	if form.process().accepted:
         for tb in ['biosource','plant_growth_condition','treatments','harvests','extraction_preparation','gas_chromatography','liquid_chromatography','mass_spectroscopy','spectrophotometry']:
            row = db(db[tb].sample_name==rec.id).select(db[tb].ALL).first()
            if row:
                row.update(sample_name = form.vars.id)
                sam=db[tb].insert(**db[tb]._filter_fields(row)) 
         redirect(URL('list_all_dev_projects',args=request.args[0:-2]))
	return locals() 
    redirect(URL('list_all_dev_projects',args=[]))


def my_samples():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), [])
    ]
    """ all my samples in the project with permissions to edit delete publish/unpublish samples """
    error = authenticate(auth.user.id,request.args(0),'add_sample') 
    l =  ['project','experiment.project',request.args(0)]
    if error == '':
      redirect(URL('list_all_dev_projects',args=l))
    return locals()

def list_all_samples1():
    proj_id = request.args(0)
    pub_samples = db((db.sample.working_status == 1)&(db.sample.project == proj_id)).select(db.sample.ALL)
    dev_samples = db((db.sample.working_status == 0)&(db.sample.project == proj_id)).select(db.sample.ALL)
    return locals()

def view_published_samples():
    proj_id = request.args(0)
    return locals() 

def router():
    l=request.args
    if 'biosource' in l:
      redirect(URL('insert_biosource',args = l))
    elif 'plant_growth_condition' in l:
      redirect(URL('insert_pgc',args = l))
    elif 'treatments' in l:
      redirect(URL('insert_treatments',args = l))
    elif 'harvests' in l:
      redirect(URL('insert_harvests',args = l))
    elif 'extraction_preparation' in l:
      redirect(URL('insert_ep',args = l))
    elif 'gas_chromatography' in l:
        redirect(URL('insert_gc',args = l))
    elif 'liquid_chromatography' in l:
        redirect(URL('insert_lc',args = l))
    elif 'mass_spectroscopy' in l:
        redirect(URL('insert_ms',args = l))
    elif 'raw_data_storage_information' in l:
          redirect(URL('insert_raw_data',args = l))
    elif 'spectrophotometry' in l:
          redirect(URL('insert_spectrophotometry',args = l))
    elif 'sample' in l and 'new' in l:
          samp = db(db.sample.experimentalist==auth.user.id).select().last()
          if samp:
           copy(samp.id)
           return()
          else: 
           return() 
    elif 'sample' in l and 'view' in l:		
        redirect(URL('sample',args=l))
    elif 'project' in l and 'view' in l and 'experiment' not in l:
        redirect(URL('project_viewer',args=l[-1]))
        
    else:
        return()

'''	elif 'sample' in l and 'new' in l:		
	  redirect(URL('add_sample',args = l))
	elif 'sample' in l:		
	  redirect(URL('sample_viewer',args = l))
	elif 'project' in l:
	  redirect(URL('project_viewer',args=l))
	else : 
	  redirect(URL('index'))'''

def list_all_pub_samples():
#    proj_id = request.args(0)
#    pub = request.args(1) # if pub == 1 show published samples otherwise non published samples
#   pub_query = (db.sample.working_status == 1 and db.sample.project == proj_id)
#   unpub_query = (db.sample.working_status == 0 and db.sample.project == proj_id)
#   pquery_dict = {'sample':pub_query}
#   nquery_dict = {'sample':unpub_query}
#    if 'view' in request.args or 'edit' in request.args or 'new' in request.args:
#       router(request.args)
#    if 'view' in request.args or 'edit' in request.args or 'new' in request.args:
#     	router(request.args)
    
    """an argument to display published and non-published samples"""
    """ request.args(0) - project  , request.args(1) published"""

    redirect(URL('list_all_pub_projects',args=['project','experiment.project',request.args(0)]))
    
def list_all_dev_samples():
   
    redirect(URL('list_all_dev_projects',args=['project','sample.project',request.args(0)]))
    return locals()

def ajx_role():
    """ an ajax call back which takes care of insert , update and delete in the roles table """
    rid = request.args(1)
    if request.args(0) == 'accept':
       row = db(db.role.id == rid).update(approval_status = 1)
       result = db(db.role.id == rid).select(db.role.ALL).first()
       gid = auth.id_group(role_list[int(result.role)])
       auth.add_membership(gid,result.user)
       row_email = db(db.auth_user.id==result.user).select(db.auth_user.ALL).first()
       mail.send(to=[row_email.email],
	                subject='Role Approved',
			          # If reply_to is omitted, then mail.settings.sender is used
				            #reply_to='us@example.com',
					              message=str(result))
    if request.args(0) == 'unblock':
       del db.role[rid] 
    if request.args(0) == 'block':
       row = db(db.role.id == rid).update(approval_status = 2)
    if request.args(0) == 'delete' or request.args(0) == 'deny':
       result = db(db.role.id == rid).select(db.role.ALL).first()
       gid = auth.id_group(role_list[int(result.role)])
       auth.del_membership(gid,result.user)
       del db.role[rid] 
    return locals()

def reg_project():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), []),
    (T('Project'), False, URL('default','project_viewer',args=request.args),[])
    ]
    """ takes an id for the project and registers """
    import datetime
    now = datetime.datetime.now()
    """ already requested """
    pid = request.args(0)
    co_mail_row = db(db.project.id==pid)(db.project.project_coordinator==db.auth_user.id).select().first()
    co_mail = co_mail_row.auth_user.email
    ptitle = db(db.project.id == pid).select(db.project.ALL).first()
    form = SQLFORM(db.role,fields=['role'],showid=False)
    if form.validate():
       requested = db(db.role.user == auth.user.id)(db.role.project == pid)(db.role.approval_status == 0)(db.role.role==form.vars.role).count()
       if requested == 0:
        mail.send(to=[co_mail],
	          subject='New Project Role Approval',
				                message='Hi, '+auth.user.first_name+' has applied for a role in the project ' + ptitle.name)
        db.role.insert(user=auth.user.id,approval_status=0,project=pid,member_since=now,role=form.vars.role)
        response.flash = 'wait for Coordinator\'s approval'
       else:
        response.flash = 'You already hold the applied role' 
    return locals() 

def ajx_publish():
    """ an ajax call back which takes care of publication status """
    eid = request.args(1)
    if request.args(0) == 'publish':
     row = db(db.project.id == eid).update(project_status = "1",project_publication_date = now)
     redirect(URL('project_viewer',args = ['Published',eid]))
    elif request.args(0) == 'unpublish':
     row = db(db.project.id == eid).update(project_status = "0",project_publication_date= None)
     redirect(URL('project_viewer',args = ['Unpublished',eid]))
    return locals() 

def roles():
    response.menu = [
    (T('Home'), False, URL('default','list_all_projects'), []),
    (T('Project'), False, URL('default','project_viewer',args=request.args),[])
    ]
    """ complete interface for managing roles for a particular project"""
    """ should be accessible to only project co-ordinators """
    pid = request.args(0)
    error = authenticate(auth.user.id,pid,'roles')
    accepted = db(db.auth_user.id == db.role.user)(db.role.approval_status == 1)(db.role.project == pid).select(db.role.ALL,db.auth_user.ALL)
    pending = db(db.auth_user.id == db.role.user)(db.role.approval_status == 0)(db.role.project == pid).select(db.role.ALL,db.auth_user.ALL)
    blocked = db(db.auth_user.id == db.role.user)(db.role.approval_status == 2)(db.role.project == pid).select(db.role.ALL,db.auth_user.ALL)
    return locals()
   
def home_page():
    """ home page for a user , shows list of projects he is working on and his past work """
    uid = request.args(0)
    #my roles 
    
    roles = db(db.role.user == uid)(db.role.project == db.project.id).select(db.role.ALL,db.project.name) 
    myroles = [role_list[int(p.role.role)] for p in roles]
    k = {}
    """
    is_coordinator = db(db.project.project_coordinator==uid).select(db.project.ALL)
    coordinating_projects = [row.name for row in is_coordinator]
    value=''
    for p in coordinating_projects:
       value = value + ','+ p
	  
    k[6] = value[1:] """
    for row in roles:
       if row.role.role not in k:
          k[row.role.role] = row.project.name
       else:
          k[row.role.role] = k[row.role.role] + ',' + row.project.name
    com_exps = db(db.sample.working_status == 1)(db.sample.experimentalist == uid)(db.sample.project == db.project.id).select(db.sample.ALL,db.project.id,db.project.name,orderby=db.sample.code)
    incom_exps = db(db.sample.working_status == 1)(db.sample.experimentalist == uid)(db.sample.project == db.project.id).select(db.sample.ALL,db.project.id,db.project.name,orderby=db.sample.code)
    pub_exps = db(db.sample.working_status == 0)(db.sample.publication_status == True)(db.sample.experimentalist == uid)(db.sample.project == db.project.id).select(db.sample.ALL,db.project.id,db.project.name,orderby=db.sample.code)
    unpub_exps = db(db.sample.working_status == 0)(db.sample.publication_status == False) (db.sample.experimentalist == uid)(db.sample.project == db.project.id).select(db.sample.ALL,db.project.id,db.project.name,orderby=db.sample.code)
    for p in k:
       list_projects = k[p].split(',')
       proj = '' 
       for d in list_projects:
          res = db(db.project.name == d).select(db.project.ALL).first()
          cat = ''
          if res:
             cat = A(res.name,_href=URL('project_viewer',args=res.id))
          if proj == '':
             proj=SPAN(cat)
          else:
           proj = SPAN(proj,',',cat)
       k[p] = proj 
    return locals()

def download():
    return response.download(request, db)

def insert_biosource():
#prepopulating records  
   if 'clear' not in request.args and 'new' in request.args:    
    trows = db(db.template.user==auth.user.id).select()
    count = db(db.template.user==auth.user.id).count()
    if count > 0:
     rows = db(db.biosource.sample_name==trows[0].sample).select()
     count1 = db(db.biosource.sample_name==trows[0].sample).count()
     if count1 > 0:
      row = rows[0]      
      for fieldname in db.biosource.fields:
       if fieldname!='id': 
        db.biosource[fieldname].default=row[fieldname]
   elif 'clear' in request.args: 
    request.args.pop()
   #result = db(db.sample.id == request.args[-3]).select(db.sample.ALL).first()
#  error = authenticate(auth.user.id,result.project,'insert_biosource')
   response.menu = [
   (T('Home'), False, URL('default','list_all_projects'), [])
   ]
   redirect_args = request.args[0:-3]
   form = SQLFORM(db.biosource,style='bootstrap')
   if 'view' in request.args: 
	       form=SQLFORM(db.biosource,request.args[-1],readonly = True,showid=False)	  
   elif 'edit' in request.args: 
	       form=SQLFORM(db.biosource,request.args[-1],showid=False)
   elif 'new' in request.args:
               db.biosource.sample_name.readable = False 
               hid = {}   
	       form=SQLFORM(db.biosource,showid=False)
	       form.vars.sample_name = request.args[-3]
 	       redirect_args = request.args[0:-4]
   i=1
   f1=form[0][:i+2]
   fs1=form[0][i+2:i+9]
   f2=form[0][i+9:]
   form[0]=TABLE(TABLE(f1),
      FIELDSET(TAG.legend("Genotype"),TABLE(fs1)),TABLE(f2))
   if form.process().accepted:
     redirect(URL('list_all_dev_projects',args=redirect_args)) 
     response.flash="Inserted entry"
   return locals()

def insert_pgc():
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.plant_growth_condition.sample_name==trows[0].sample).select()
    count1 = db(db.plant_growth_condition.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.plant_growth_condition.fields:
      if fieldname!='id': 
       db.plant_growth_condition[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  form = SQLFORM(db.plant_growth_condition) 
  if 'view' in request.args: 
	form=SQLFORM(db.plant_growth_condition,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  elif 'edit' in request.args: 
	form=SQLFORM(db.plant_growth_condition,request.args[-1],upload=URL('download'),showid=False)
  elif 'new' in request.args:
        db.plant_growth_condition.sample_name.readable = False 
	form=SQLFORM(db.plant_growth_condition,showid=False)
        form.vars.sample_name = request.args[-3]
	redirect_args = request.args[0:-2]	 
  i=1
  fs1=form[0][:i+5]
  fss1=form[0][i+5:i+9]
  fss2=form[0][i+9:i+10]
  fss3=form[0][i+10:i+15]
  f2=form[0][i+15:i+18]
  fs2=form[0][i+18:i+21]
  fs3=form[0][i+21:i+27]
  f3=form[0][i+27:]
  t2=TABLE(FIELDSET(TAG.legend("Growth Support"),TABLE(fs1)))
  t3=TABLE(FIELDSET(TAG.legend("Location"),TABLE(FIELDSET(TAG.legend("Field trail"),TABLE(fss1))),TABLE(fss2),TABLE(FIELDSET(TAG.legend("Green house"),TABLE(fss3)))))
  t4=TABLE(FIELDSET(TAG.legend("Nutritional Regime"),TABLE(fs2)))
  t5=TABLE(FIELDSET(TAG.legend("Date of Plant Establishment(YYYY-MM-DD)"),TABLE(fs3)))
  form[0]=TABLE(FIELDSET(t2,t3,TABLE(f2),t4,t5,TABLE(f3)))
  if form.process().accepted:
    redirect(URL('list_all_dev_projects',args=redirect_args)) 
    response.flash="form accepted"
# redirect(URL('list_all_samples',args=['sample'])) 
  else:
    response.flsh="form has some errors"
  return locals()

def insert_ep():
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.extraction_preparation.sample_name==trows[0].sample).select()
    count1 = db(db.extraction_preparation.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.extraction_preparation.fields:
      if fieldname!='id': 
       db.extraction_preparation[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
       form=SQLFORM(db.extraction_preparation,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  if 'edit' in request.args: 
       form=SQLFORM(db.extraction_preparation,request.args[-1],upload=URL('download'),showid=False)
  if 'new' in request.args:
       db.extraction_preparation.sample_name.readable=False
       form=SQLFORM(db.extraction_preparation,showid=False)
       form.vars.sample_name = request.args[-3]
       redirect_args = request.args[0:-2]	 
  i=3
  t1=TABLE(FIELDSET(TAG.legend("SAMPLE EXTRACTION"),TABLE(form[0][:i+8]),TABLE(FIELDSET(TAG.legend("Extract Storage:"),TABLE(form[0][i+8:i+12])))))
  t2=TABLE(FIELDSET(TAG.legend("SAMPLE PREPARATION"),TABLE(form[0][i+12:])))
  form[0]=TABLE(FIELDSET(t1,t2))
  if form.process().accepted:
       response.flash="Inserted entry"
       redirect(URL('list_all_dev_projects',args=redirect_args)) 
  return locals()

def insert_treatments():
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.treatments.sample_name==trows[0].sample).select()
    count1 = db(db.treatments.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.treatments.fields:
      if fieldname!='id': 
       db.treatments[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
       form=SQLFORM(db.treatments,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  if 'edit' in request.args: 
       form=SQLFORM(db.treatments,request.args[-1],upload=URL('download'),showid=False)
  if 'new' in request.args:
       db.treatments.sample_name.readable=False
       form=SQLFORM(db.treatments,showid=False)
       form.vars.sample_name = request.args[-3] 
       redirect_args = request.args[0:-2]	 
  i=1
  t1=TABLE(FIELDSET(TAG.legend("Treatment Factor"),TABLE(form[0][:i+3])))
  form[0]=TABLE(FIELDSET(t1,TABLE(form[0][i+3:])))
  if form.process().accepted:
      response.flash="Inserted entry"
      redirect(URL('list_all_dev_projects',args=redirect_args)) 
  return locals()

def insert_harvests():
  form = ''	
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.harvests.sample_name==trows[0].sample).select()
    count1 = db(db.harvests.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.harvests.fields:
      if fieldname!='id': 
       db.harvests[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
       form=SQLFORM(db.harvests,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  if 'edit' in request.args: 
       form=SQLFORM(db.harvests,request.args[-1],upload=URL('download'),showid=False)
  if 'new' in request.args:
       db.harvests.sample_name.readable=False
       form=SQLFORM(db.harvests,showid=False)
       form.vars.sample_name = request.args[-3]
       redirect_args = request.args[0:-2]
  i=1	 
  t1=TABLE(FIELDSET(TAG.legend("Sample Storage"),TABLE(form[0][i+7:])))
  form[0]=TABLE(FIELDSET(TABLE(form[0][:i+7]),t1))
  if form.process().accepted:
      response.flash="Inserted entry"
      redirect(URL('list_all_dev_projects',args=redirect_args)) 
  return locals()
	  	
def insert_gc():
#prepopulating records  
  form = ''
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.gas_chromatography.sample_name==trows[0].sample).select()
    count1 = db(db.gas_chromatography.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.gas_chromatography.fields:
      if fieldname!='id': 
       db.gas_chromatography[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
	form=SQLFORM(db.gas_chromatography,request.args[-1],readonly = True,pload=URL('download'),showid=False)
  elif 'edit' in request.args: 
        form=SQLFORM(db.gas_chromatography,request.args[-1],upload=URL('download'),showid=False)
  elif 'new' in request.args:
        db.gas_chromatography.sample_name.readable=False
        redirect_args = request.args[0:-2]	 
        form=SQLFORM(db.gas_chromatography,showid=False)
        form.vars.sample_name = request.args[-3]
  j=1
  t_ep_1=TABLE(FIELDSET(TAG.legend("SAMPLE EXTRACTION"),TABLE(form[0][:j+7]),TABLE(FIELDSET(TAG.legend("Extract Storage:"),TABLE(form[0][j+7:j+11])))))
  t_ep_2=TABLE(FIELDSET(TAG.legend("SAMPLE PREPARATION"),TABLE(form[0][j+11:15])))
  i=15
  t1=TABLE(FIELDSET(TAG.legend("CHROMATOGRAPHY INSTRUMENTAL"),TABLE(form[0][15:i+4])))
  t2=TABLE(FIELDSET(TAG.legend("DERIVATIZATION"),TABLE(form[0][i+4:i+8])))
  t3=TABLE(FIELDSET(TAG.legend("AUTO-INJECTOR DETAILS"),TABLE(form[0][i+8:i+15])))
  t4=TABLE(FIELDSET(TAG.legend("SEPERATION COLUMN AND PRE/GUARD COLUMN"),TABLE(form[0][i+15:i+23])))
  t5=TABLE(FIELDSET(TAG.legend("SEPERATION PARAMETERS"),TABLE(form[0][i+23:i+30])))
  t6=TABLE(FIELDSET(TAG.legend("QUALITY CONTROL"),TABLE(form[0][i+30:i+34]),TABLE(FIELDSET(TAG.legend("Cycle per"),TABLE(form[0][i+34:i+39])))))
  t7=TABLE(FIELDSET(TAG.legend("DATA ACQUISITION"),TABLE(form[0][i+39:])))
  form[0]=TABLE(FIELDSET(t_ep_1,t_ep_2,t1,t2,t3,t4,t5,t6,t7))
  if form.process().accepted:
	response.flash="Inserted entry"
	redirect(URL('list_all_dev_projects',args=redirect_args)) 
#       redirect(URL('list_all_samples',args=['sample'])) 
  return locals()

def insert_lc():
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.liquid_chromatography.sample_name==trows[0].sample).select()
    count1 = db(db.liquid_chromatography.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.liquid_chromatography.fields:
      if fieldname!='id': 
       db.liquid_chromatography[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  form = SQLFORM(db.liquid_chromatography)
  if 'view' in request.args: 
      form=SQLFORM(db.liquid_chromatography,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  if 'edit' in request.args: 
      form=SQLFORM(db.liquid_chromatography,request.args[-1],upload=URL('download'),showid=False)
  if 'new' in request.args:
      db.liquid_chromatography.sample_name.readable=False
      redirect_args = request.args[0:-2]	 
      form=SQLFORM(db.liquid_chromatography,showid=False)
      form.vars.sample_name = request.args[-3] 
  j=1
  t_ep_1=TABLE(FIELDSET(TAG.legend("SAMPLE EXTRACTION"),TABLE(form[0][:j+7]),TABLE(FIELDSET(TAG.legend("Extract Storage:"),TABLE(form[0][j+7:j+11])))))
  t_ep_2=TABLE(FIELDSET(TAG.legend("SAMPLE PREPARATION"),TABLE(form[0][j+11:15])))
  i=15
  t1=TABLE(FIELDSET(TAG.legend("CHROMATOGRAPHY INSTRUMENTAL"),TABLE(form[0][15:i+4])))
  t3=TABLE(FIELDSET(TAG.legend("AUTO-INJECTOR DETAILS"),TABLE(form[0][i+4:i+11])))
  t4=TABLE(FIELDSET(TAG.legend("SEPERATION COLUMN AND PRE/GUARD COLUMN"),TABLE(form[0][i+11:i+19])))
  t5=TABLE(FIELDSET(TAG.legend("SEPERATION PARAMETERS"),TABLE(form[0][i+19:i+26])))
  t6=TABLE(FIELDSET(TAG.legend("QUALITY CONTROL"),TABLE(form[0][i+26:i+30]),TABLE(FIELDSET(TAG.legend("Cycle per"),TABLE(form[0][i+30:i+35])))))
  t7=TABLE(FIELDSET(TAG.legend("DATA ACQUISITION"),TABLE(form[0][i+35:])))
  form[0]=TABLE(FIELDSET(t_ep_1,t_ep_2,t1,t3,t4,t5,t6,t7))
  if form.process().accepted:
      response.flash="Inserted entry"
      redirect(URL('list_all_dev_projects',args=redirect_args)) 
#     redirect(URL('list_all_samples',args=['sample'])) 
  return locals()

def insert_ms():
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.mass_spectroscopy.sample_name==trows[0].sample).select()
    count1 = db(db.mass_spectroscopy.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.mass_spectroscopy.fields:
      if fieldname!='id': 
       db.mass_spectroscopy[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  #result = db(db.sample.id == request.args[-1]).select(db.sample.ALL).first()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
    form=SQLFORM(db.mass_spectroscopy,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  elif 'edit' in request.args: 
    form=SQLFORM(db.mass_spectroscopy,request.args[-1],upload=URL('download'),showid=False)
  elif 'new' in request.args:
    db.mass_spectroscopy.sample_name.readable=False
    redirect_args = request.args[0:-2]	 
    form=SQLFORM(db.mass_spectroscopy,showid=False)
    form.vars.sample_name = request.args[-3]
  i=1
  t1=TABLE(FIELDSET(TAG.legend("INSTRUMENTAL DETAILS"),TABLE(form[0][:i+4])))
  t2=TABLE(FIELDSET(TAG.legend("IONISATION SOURCE"),TABLE(form[0][i+4:i+10])))
  t3=TABLE(FIELDSET(TAG.legend("MASS ANALYZER"),TABLE(form[0][i+10:i+18]),TABLE(FIELDSET(TAG.legend("Lock spray"),TABLE(form[0][i+18:i+22]))),TABLE(form[0][i+22:i+23])))
  t4=TABLE(FIELDSET(TAG.legend("QUALITY CONTROL"),TABLE(form[0][i+23:i+27])))
  t5=TABLE(FIELDSET(TAG.legend("DATA ACQUISITION"),TABLE(form[0][i+27:])))
  form[0]=TABLE(FIELDSET(t1,t2,t3,t4,t5))
  if form.process().accepted:
      	response.flash="Inserted entry"
        redirect(URL('list_all_dev_projects',args=redirect_args)) 
#     	redirect(URL('list_all_samples'),args=['sample']) 
  return locals()

def insert_raw_data():
#prepopulating records  
  if False:    
    trows = db(db.template.user==auth.user.id).select()
    count = db(db.template.user==auth.user.id).count()
    if count > 0:
      rows = db(db.raw_data_storage_information.sample_name==trows[0].sample).select()
      count1 = db(db.raw_data_storage_information.sample_name==trows[0].sample).count()
      if count1 > 0:
       row = rows[0]
       for fieldname in db.raw_data_storage_information.fields:
        if fieldname!='id': 
         db.raw_data_storage_information[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
    form=SQLFORM(db.raw_data_storage_information,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  elif 'edit' in request.args: 
    form=SQLFORM(db.raw_data_storage_information,request.args[-1],upload=URL('download'),showid=False)
  elif 'new' in request.args:
    db.raw_data_storage_information.sample_name.readable=False
    redirect_args = request.args[0:-2]	 
    form=SQLFORM(db.raw_data_storage_information,showid=False)
    form.vars.sample_name = request.args[-3]
    form.vars.email_id_of_person=auth.user.email 
  if form.process().accepted:
      	response.flash="Inserted entry"
        redirect(URL('list_all_dev_projects',args=redirect_args)) 
#     	redirect(URL('list_all_samples'),args=['sample']) 
  return locals()

def insert_spectrophotometry():
#prepopulating records  
  if 'clear' not in request.args and 'new' in request.args:    
   trows = db(db.template.user==auth.user.id).select()
   count = db(db.template.user==auth.user.id).count()
   if count > 0:
    rows = db(db.spectrophotometry.sample_name==trows[0].sample).select()
    count1 = db(db.spectrophotometry.sample_name==trows[0].sample).count()
    if count1 > 0:
     row = rows[0]
     for fieldname in db.spectrophotometry.fields:
      if fieldname!='id': 
       db.spectrophotometry[fieldname].default=row[fieldname]
  elif 'clear' in request.args: 
    request.args.pop()
  response.menu = [
  (T('Home'), False, URL('default','list_all_projects'), [])
  ]
  redirect_args = request.args[0:-3]	 
  if 'view' in request.args: 
    form=SQLFORM(db.spectrophotometry,request.args[-1],readonly = True,upload=URL('download'),showid=False)
  elif 'edit' in request.args: 
    form=SQLFORM(db.spectrophotometry,request.args[-1],upload=URL('download'),showid=False)
  elif 'new' in request.args:
    db.spectrophotometry.sample_name.readable=False
    redirect_args = request.args[0:-2]	 
    form=SQLFORM(db.spectrophotometry,showid=False)
    form.vars.sample_name = request.args[-3]
  if form.process().accepted:
      	response.flash="Inserted entry"
        redirect(URL('list_all_dev_projects',args=redirect_args)) 
#     	redirect(URL('list_all_samples'),args=['sample']) 
  return locals()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

#def drop_tables():
    #are you sure you want to do this?
    #for t in ['auth_user','auth_group', 'auth_membership', 'auth_permission', 'auth_event','sample','biosource','affiliation','project','role','template','experiment','project_meta','plant_growth_condition','treatments','harvests','extraction_preparation','gas_chromatography','liquid_chromatography','mass_spectroscopy','spectrophotometry','feedback','sample_files']:
    #    db[t].drop()
    # pass
    #return 

def show_feedback():
    grid = SQLFORM.smartgrid(db.feedback)
    return locals()

 
def post_feedback():
    """ allows to post feedback to the table feedback """ 
    past_feeds = db(db.feedback.feedback_on == request.env.http_referer).select(db.feedback.feedback_body,db.feedback.id)
    form = SQLFORM(db.feedback,fields=['feedback_body'],labels={'feedback_body':'Your feedback about this page'})
    feedback_by = ''
    if form.validate():
	if auth.user:
            feedback_by = auth.user.id
        else:
	   feedback_by = ''
	db.feedback.insert(feedback_on=request.env.http_referer,feedback_body=form.vars.feedback_body,feedback_by=feedback_by)
	response.flash = "feedback has been duly noted and will be taken care of "
    return locals()


def user_viewer():
   """shows the user details """
   uid = request.args(0)
   record = db.auth_user(uid)
   form = SQLFORM(db.auth_user,record,readonly=True,showid=False,fields=['first_name','last_name','email','affiliated_to','phone','mobile','city'])
   return locals()


def dict_dump(obj,inp):
  ans = '<dl class="dl-horizontal">'
  for key in inp.keys():
     add = '<dt>'+str(inp[key])+'</dt>'+'<dd>'+str(obj[key])+'</dd>'
     ans = ans+add
  return ans	


def sample():
  """gets all the information regarding a sample in a single page """
  sid = request.args[-1]
  sample = db(db.sample.id == sid).select(db.sample.ALL).first()
  user = db(db.auth_user.id == sample.experimentalist).select(db.auth_user.ALL).first()
  experiment = db(db.experiment.id == sample.experiment).select(db.experiment.ALL).first()
  biosource = db(db.biosource.sample_name == sid).select(db.biosource.ALL)
  plant_growth = db(db.plant_growth_condition.sample_name == sid).select(db.plant_growth_condition.ALL)
  treatment = db(db.treatments.sample_name == sid).select(db.treatments.ALL)
  harvest = db(db.harvests.sample_name == sid).select(db.harvests.ALL)
  extraction_preparation = db(db.extraction_preparation.sample_name == sid).select(db.extraction_preparation.ALL)
  gc = db(db.gas_chromatography.sample_name == sid).select(db.gas_chromatography.ALL)
  lc = db(db.liquid_chromatography.sample_name == sid).select(db.liquid_chromatography.ALL)
  ms = db(db.mass_spectroscopy.sample_name == sid).select(db.mass_spectroscopy.ALL)
  raw_storage = db(db.raw_data_storage_information.sample_name == sid).select(db.raw_data_storage_information.ALL)
  biosource_forms = [] #a list of forms
  for each in biosource:
	form = SQLFORM(db.biosource,each.id,showid=False,readonly=True)
	i=1
	f1=form[0][:i+2]
	fs1=form[0][i+2:i+7]
	f2=form[0][i+7:]
	form[0]=TABLE(TABLE(f1),FIELDSET(TAG.legend("Genotype"),TABLE(fs1)),TABLE(f2))
	biosource_forms.append(form[0])
        
  pgc_forms = []
  for each in plant_growth:
     form = SQLFORM(db.plant_growth_condition,each.id,showid=False,readonly=True)
     i=1
     fs1=form[0][:i+5]
     fss1=form[0][i+5:i+9]
     fss2=form[0][i+9:i+10]
     fss3=form[0][i+10:i+15]
     f2=form[0][i+15:i+18]
     fs2=form[0][i+18:i+21]
     fs3=form[0][i+21:i+27]
     f3=form[0][i+27:]
     t2=TABLE(FIELDSET(TAG.legend("Growth Support"),TABLE(fs1)))
     t3=TABLE(FIELDSET(TAG.legend("Location"),TABLE(FIELDSET(TAG.legend("Field trail"),TABLE(fss1))),TABLE(fss2),TABLE(FIELDSET(TAG.legend("Green house"),TABLE(fss3)))))
     t4=TABLE(FIELDSET(TAG.legend("Nutritional Regime"),TABLE(fs2)))
     t5=TABLE(FIELDSET(TAG.legend("Date of Plant Establishment(YYYY-MM-DD)"),TABLE(fs3)))
     form[0]=TABLE(FIELDSET(t2,t3,TABLE(f2),t4,t5,TABLE(f3)))
     pgc_forms.append(form[0])
  
  treatment_forms = []
  for each in treatment:
     form = SQLFORM(db.treatments,each.id,showid=False,readonly=True)
     i=1
     t1=TABLE(FIELDSET(TAG.legend("Treatment Factor"),TABLE(form[0][:i+3])))
     form[0]=TABLE(FIELDSET(t1,TABLE(form[0][i+3:])))


  harvest_forms = []
  for each in harvest:
     form = SQLFORM(db.harvests,each.id,showid=False,readonly=True)
     i=1
     t1=TABLE(FIELDSET(TAG.legend("Sample Storage"),TABLE(form[0][i+7:])))
     form[0]=TABLE(FIELDSET(TABLE(form[0][:i+7]),t1))
     harvest_forms.append(form[0])

  gc_forms = []
  for each in gc:
     form = SQLFORM(db.gas_chromatography,each.id,showid=False,readonly=True)
     j=1
     t_ep_1=TABLE(FIELDSET(TAG.legend("SAMPLE EXTRACTION"),TABLE(form[0][:j+7]),TABLE(FIELDSET(TAG.legend("Extract Storage:"),TABLE(form[0][j+7:j+11])))))
     t_ep_2=TABLE(FIELDSET(TAG.legend("SAMPLE PREPARATION"),TABLE(form[0][j+11:15])))
     i=15
     t1=TABLE(FIELDSET(TAG.legend("CHROMATOGRAPHY INSTRUMENTAL"),TABLE(form[0][15:i+4])))
     t2=TABLE(FIELDSET(TAG.legend("DERIVATIZATION"),TABLE(form[0][i+4:i+8])))
     t3=TABLE(FIELDSET(TAG.legend("AUTO-INJECTOR DETAILS"),TABLE(form[0][i+8:i+15])))
     t4=TABLE(FIELDSET(TAG.legend("SEPERATION COLUMN AND PRE/GUARD COLUMN"),TABLE(form[0][i+15:i+23])))
     t5=TABLE(FIELDSET(TAG.legend("SEPERATION PARAMETERS"),TABLE(form[0][i+23:i+30])))
     t6=TABLE(FIELDSET(TAG.legend("QUALITY CONTROL"),TABLE(form[0][i+30:i+33]),TABLE(FIELDSET(TAG.legend("Cycle per"),TABLE(form[0][i+33:i+37])))))
     t7=TABLE(FIELDSET(TAG.legend("DATA ACQUISITION"),TABLE(form[0][i+37:])))
     form[0]=TABLE(FIELDSET(t_ep_1,t_ep_2,t1,t2,t3,t4,t5,t6,t7))

     gc_forms.append(form[0])
 
  lc_forms = []
  
  for each in lc:
    form = SQLFORM(db.gas_chromatography,each.id,showid=False,readonly=True)
    j=1
    t_ep_1=TABLE(FIELDSET(TAG.legend("SAMPLE EXTRACTION"),TABLE(form[0][:j+7]),TABLE(FIELDSET(TAG.legend("Extract Storage:"),TABLE(form[0][j+7:j+11])))))
    t_ep_2=TABLE(FIELDSET(TAG.legend("SAMPLE PREPARATION"),TABLE(form[0][j+11:15])))
    i=15
    t1=TABLE(FIELDSET(TAG.legend("CHROMATOGRAPHY INSTRUMENTAL"),TABLE(form[0][15:i+4])))
    t3=TABLE(FIELDSET(TAG.legend("AUTO-INJECTOR DETAILS"),TABLE(form[0][i+4:i+11])))
    t4=TABLE(FIELDSET(TAG.legend("SEPERATION COLUMN AND PRE/GUARD COLUMN"),TABLE(form[0][i+11:i+19])))
    t5=TABLE(FIELDSET(TAG.legend("SEPERATION PARAMETERS"),TABLE(form[0][i+19:i+26])))
    t6=TABLE(FIELDSET(TAG.legend("QUALITY CONTROL"),TABLE(form[0][i+26:i+29]),TABLE(FIELDSET(TAG.legend("Cycle per"),TABLE(form[0][i+29:i+33])))))
    t7=TABLE(FIELDSET(TAG.legend("DATA ACQUISITION"),TABLE(form[0][i+33:])))
    form[0]=TABLE(FIELDSET(t_ep_1,t_ep_2,t1,t3,t4,t5,t6,t7))
    lc_forms.append(form[0])
 
  ms_forms = []
  for each in ms:
    form = SQLFORM(db.mass_spectroscopy,each.id,showid=False,readonly=True)
    i=1
    t1=TABLE(FIELDSET(TAG.legend("INSTRUMENTAL DETAILS"),TABLE(form[0][:i+4])))
    t2=TABLE(FIELDSET(TAG.legend("IONISATION SOURCE"),TABLE(form[0][i+4:i+10])))
    t3=TABLE(FIELDSET(TAG.legend("MASS ANALYZER"),TABLE(form[0][i+10:i+18]),TABLE(FIELDSET(TAG.legend("Lock spray"),TABLE(form[0][i+18:i+22]))),TABLE(form[0][i+22:i+23])))
    t4=TABLE(FIELDSET(TAG.legend("QUALITY CONTROL"),TABLE(form[0][i+23:i+27])))
    t5=TABLE(FIELDSET(TAG.legend("DATA ACQUISITION"),TABLE(form[0][i+27:])))
    form[0]=TABLE(FIELDSET(t1,t2,t3,t4,t5))  
    ms_forms.append(form[0])

  raw_forms = []
  for each in raw_storage:
     form = SQLFORM(db.raw_data_storage_information,each.id,showid=False,readonly=True)
     raw_forms.append(form[0])


  return locals() 

#def grid():
  # query=((db.project.project_status==0)&(db.experiment.project==db.project.id)&(db.sample.experiment==db.experiment.id)&(db.biosource.sample_name==db.sample.id))
   #query=((db.sample.project==db.project.id)&(db.project.id>0))
   #query=((db.project.id>0)&(db.sample.project==db.project.id)&((db.sample.id==db.biosource.sample_name)&(db.sample.id==db.plant_growth_condition.sample_name)))
#   query=((db.sample.experiment==db.experiment.id)&((db.sample.id==db.biosource.sample_name)|(db.sample.id==db.plant_growth_condition.sample_name)))
#   grid = SQLFORM.grid(query)
#   return locals()


def search():
    form=FORM('Your name:',
              INPUT(_name='name', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.accepts(request,session):
      redirect(URL('sample',args=form.vars.name)) 
    return locals()
    
def multiple_files():
   """allows an experimentalist to add multiple images and files and displays it in the consolidated sample view form """
   """ per sample . takes id of the sample as the input """
   sid = request.args(0)
   sample = db(db.sample.id == sid).select().first() 
   old = db(db.sample_files.sample == sid).select(db.sample_files.ALL)
   form = SQLFORM(db.sample_files)
   form.vars.sample = sid
   form.vars.user= auth.user.id 
   if form.process().accepted:
      response.flash = 'File added'
   elif form.errors:
      response.flash = 'Errors in form please check it out'
   return locals()


