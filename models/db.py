﻿#s scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.db')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables




db.define_table('affiliation',
		Field('name','string',required=True,requires=IS_NOT_EMPTY()),
		Field('description','text',required=True),format='%(name)s')


auth.settings.extra_fields['auth_user'] = [
     Field('title',notnull=True,required=True,requires=IS_IN_SET({'0':'Mr','1':'Mrs','2':'Ms','3':'Prof','4':'Dr'}),label = 'Salutation'),
     Field('position',notnull=False,label='Positon',required=True,requires=IS_IN_SET({'0':'Post Doctoral Fellow','1':'Scientist','2':'Post Graduate/Phd student','3':'Under Graduate','4':'Faculy/Project Co-ordinator'})),
#     Field('middle',notnull=False,required=False,label='Middle Name'),
     Field('affiliated_to',requires=IS_NOT_EMPTY(),label = 'Affiliation'),
     Field('address','text', label='Postal Address',required=True,requires = IS_NOT_EMPTY()),
     Field('city',notnull=False,required=True,requires=IS_NOT_EMPTY(),label = 'City'),
     Field('country',notnull=True,required=True,requires=IS_NOT_EMPTY(),default = 'India',label = 'Country'),
     Field('postal_code',notnull=True,required=True,requires=IS_NOT_EMPTY(),label = 'Postal Code'),
     Field('phone',label = 'Telephone Number'),
     Field('mobile',notnull=True,required=True,requires=IS_NOT_EMPTY(),label = 'Mobile Number')
     #Field('registration_at',notnull=False,required=False,requires=IS_IN_SET({'0':'IIIT Hyderabad','1':'JNU Delhi'}),label ='Registration at',comment='centre you wish to attend for the workshop')
]
	
#auth.define_tables(username=True)
auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = 'mail.iiit.ac.in:25'
mail.settings.sender = 'metabolomics@iiit.ac.in'
#mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = False

auth.messages.verify_email = 'Click on the link http://metabolomics.iiit.ac.in/module_1_modified/default/user/verify_email'+'/%(key)s to verify your email'

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
import datetime
now = datetime.datetime.now()
today_date = datetime.datetime.today() 

role_list = ['investigator','co_investigator','collaborator','analyst','experimentalist','member','project_coordinator']

T.force('en-de')
db.auth_user._format='%(first_name)s'+' '+'%(last_name)s'

db.define_table('project',
     Field('name',notnull=True,unique=True,required=True,requires=IS_NOT_IN_DB(db,'project.name'),label='Project Name'),
     Field('code',notnull=True,unique=True,required=True,requires=IS_NOT_IN_DB(db,'project.code'),label='Project Code'),
     Field('start_date','date',default=today_date,notnull=True,required=True,requires=IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),
     Field('project_coordinator','reference auth_user'),
     Field('project_description','text',required = True,requires= IS_NOT_EMPTY(),label='Brief Description of Experiment/Project'),
     #Field('project_description_upload','upload',label='Or upload'),
     Field('project_status',notnull=True,default='0',requires=IS_IN_SET({'0':'Development','1':'Published'})),
     Field('project_literature_reference','integer',label='Literature Reference Pubmed ID (Any relevant published Document)'),
     Field('project_journal_name','string',label='Already Published Work'),
     Field('project_publication_date','date',writable=False),
     
     #Field('project_pubmed_id','string',label='PubMed ID'),
     format='%(name)s')


db.define_table('role',
     Field('user','reference auth_user'),
     Field('project','reference project'), 
     Field('role',notnull=True,required=True,requires=IS_IN_SET({'0':'Investigator','1':'Co-Investigator','2':'Collaborator','4':'Experimentalist'})),
     Field('approval_status',notnull=True,requires=IS_IN_SET({'0':'Pending','1':'Approved','2':'Blocked'})),
     Field('member_since',readable=False,writable=False,notnull=True,required=True,default=request.now))
#recent = db(db.role.user>now-datetime.timedelta(10))
#db.role.user.requires = IS_NOT_IN_DB(db,'role.user','role.role','role.project')
 
#the user and code and required time should be not null , required ..  
#added project field to sync with db.insert in controller
db.define_table('sample',
    Field('parent','reference sample',writable=False),
    Field('experimentalist','reference auth_user',writable=False),
   # Field('analyst','reference auth_user'),
    Field('name',notnull=True,required=True,label='Sample Name'),
    Field('code',required=True,label='Sample Code'),
    #requires=IS_NOT_IN_DB(db,'sample.code'),
    Field('description','text',length=2000,label='Sample Description'),
   # Field('project','reference project'),
    Field('scientific_name','string'),
    Field('grouping','reference grouping',writable=False),
    Field('working_status',default=1,required=True,requires=IS_IN_SET({'0':'Completed','1':'In Progress'})),
    Field('replica',default='Original',required=True,requires=IS_IN_SET(['Original','replicate','aliquot']),label='Type'),
    Field('publication_status','boolean',default=False,required=True,label='Pub?'),format='%(name)s',singular='Sample',plural='Samples')


db.define_table('template',
    Field('user',unique=True),
    Field('sample','reference sample'))

db.define_table('grouping',
    Field('experimentalist','reference auth_user'),
   # Field('analyst','reference auth_user'),
    Field('name',unique=True,notnull=True,required=True,label='Group Name'),
    Field('code',required=True,requires=IS_NOT_IN_DB(db,'grouping.code'),label='Group Code'),
    Field('description','text',length=2000,notnull=True,required=True,label='Group Description'),
    Field('project','reference project',writable=False),
    Field('working_status',default=1,required=True,requires=IS_IN_SET({'0':'Completed','1':'In Progress'})),
    Field('publication_status','boolean',default=False,required=True,label='Published'),format='%(name)s',singular='Group',plural='Groups')


#bio tables

#schema changes - plant_type (Inbred,Hybrid,Complete) is added 

# 2.1 
db.define_table('biosource',
    Field('sample_name','reference sample',writable = False),
    Field('species_name','string',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='Names of species to be described according to the NCBI taxonomy database (http://pubmedexpress.nih.gov/Taxonomy/taxonomyhome.html/index.cgi ). Plant species need to be named in full and not abbreviated, e.g. Arabidopsis thaliana.'),
#Genotype sub table starts         2      --> 21.3.13
    Field('genotype_echotype','string',label='Echotype/Background',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('genotype_pedigree_information','string',label='Pedigree Information',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('genotype_plant_type','string',label='Plant Type',required=True,notnull=True,requires=IS_IN_SET({'Transgenic Type','Mutant Type','Wild Type'})),
    Field('genotype_gene_names','string',label='Gene Name(s)',required=True,notnull=True),
#Genotype sub table ends           6      --->21.3.13

#Field('geno_gene_name',)
    Field('phenotype','string',label='Phenotype'),
    Field('plant_type','string',requires=IS_IN_SET({'0':'Inbred','1':'Hybrid','2':'Composite'}),label='Plant Genetic Type'),
    Field('source_of_germplasm','string',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    
    Field('organ' ,'string',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('organ_spec','string',label='Organ Specification',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='Name or description of specific part of organ if any used for the study'),
    Field('cell_type','string',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment = 'Specific plant cells used after dissection or cell sorting or any other method. This naming should be used based on Plant Ontology Consortium (POC)'),
    Field('sub_cell_location','string',label='Sub Cellular Location',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='This is about sub cellular locations from cells are collected for experiment. Naming should be maintained based on Gene Ontology Cellular Component'),
    Field('bio_source_amount','string',label='BioSource Amount',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='This is reference to the mass (mg fresh weight or mg dry weight), number of cells or other measurable quantification information'),
    Field('additional_information','text',label='Additional Information'),
    Field('other_add_info_upload','upload',label='or')
    )



#schema changes - date est other has been changed from date to text and the label has been changed
#pgc table                     -->21.3.13
db.define_table('plant_growth_condition',
    Field('sample_name','reference sample', writable = False),

# Growth support table start under pgc  1         -->21.3.13      
    Field('growth_soil','string',label='Soil (type, supplier)',),		
    Field('growth_agar','string',label='Agar (type, supplier)',),		
    Field('growth_vermiculite','string',label='Vermiculite (type, supplier)',),

# Hydro ponic system table start under growth support  4       -->21.3.13		
    Field('hydroponic_type','string',label='Type'),
    Field('hydroponic_supplier','string',label='Supplier'),
    Field('hydroponic_nutrient_concentration','string',label='Nutrient Concentration'),
    Field('hydroponic_volume','string',label='volume'),
    Field('hydroponic_number_of_plats','string',label='No. of plats/tray or container'),
    Field('hydroponic_frequency','string',label='frequency of nutrient changed'),
    Field('hydroponic_aeration_provided','boolean',label='Aeration provided(yes/No)'),

# Hydro ponic system table end under growth support   11     -->21.3.13		

    Field('growth_cell_culture','string',label='Cell culture (media,volume,cell number per volume )'),
# Growth Support table ends under pgc     12          -->21.3.13

#Location table starts under pgc   12               -->21.3.13

#Field trail table starts under location   12               -->21.3.13
    Field('loc_field_location','string',label='Location',comment='Field Location'),	
    Field('loc_field_avr_humidity','string',label='Average Humidity',),
    Field('loc_field_avr_temp','string',label='Average Temperature',),
    Field('loc_field_avr_rain','string',label='Average Rain Fall',),
    Field('season','string'),
#Field trail table ends under location   17               -->21.3.13

#Climate chamber table starts under location   17               -->21.3.13
    Field('Climate_chamber_size','string',label='Size(m3)',),
    Field('Climate_chamber_co2_concentration','string',label='Co2 concentration'),

#Climate chamber table ends under location   19               -->21.3.13

#Green house table starts under location   19               -->21.3.13
#ssss_location table starts under green house   19               -->21.3.13
    Field('loc_green_location','string',label='Location',),		

#ssss_location table ends under green house   20               -->21.3.13
#Light table starts under green house   20               -->21.3.13

    Field('loc_green_light_quality','string',label='Quality',),		
    Field('loc_green_light_source','string',label='source mode/type',),		
    Field('loc_green_light_intensity','string',label='Intensity',),		
    Field('loc_green_light_luminiscence','string',label='Luminescence light period in hrs',),		
#Light table ends under green house   24               -->21.3.13


#other columns starts under green house   24               -->21.3.13
    Field('loc_green_humidity','string',label='Humidity (day,night)',),
    Field('loc_green_temperature','string',label='Temperature (day,night)',),		
    Field('loc_green_water','string',label='Water Regime (Amount, time per day) ',),

#other columns ends under green house   27               -->21.3.13
#Green house table ends under location   27               -->21.3.13

    Field('Growth_Protocol_Description','text',label='Growth Protocol Description',comment='Detailed information about Plant Growth Conditions'),	
    Field('growth_protocol_description_upload','upload',label='or'),	
    Field('Growth_Plot_Design','text',label='Growth Plot Design',comment='The way to randomize the different genotype environment interactions. Either descriptive or using established nomenclature e.g. latin square.'),
#Nutritional regime start underpgc       30                --->23.3.13	
    Field('nutr_amount','string',label='Nutrient Amount',),		
    Field('nutr_duration','string',label='Duration',),		
    Field('nutr_add_info','text',label='Additional information',),

#Nutritional regime end underpgc       33                --->23.3.13	
#Date of planr est. start underpgc       33                --->23.3.13	
    Field('sowing_period','string'),
#,required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!',))),		
    Field('germinating_period','string'),
#,label='Date of Germination',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),
    Field('date_estimate_transplanting','string',label="Date Of Transplanting"),
#,label='Date of Transplanting',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),
    Field('date_estimate_cutting','string'),
#,label='Date of cutting',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),		
    Field('date_estimate_grafting','string'),
    
#,label='Date of Grafting ',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),	
    Field('date_est_other','string',label='Any other date',required=False),
    Field('date_other','string',label='Other appropriate time stamps,Stages etc)',required=False),	
#Date of planr est. end underpgc       39                --->23.3.13	
    Field('other_spec','text',label='Other Specific Metadata'),	
    Field('other_spec_upload','upload',label='or'),
    Field('additional_information','text',label='Additional Information'),
    Field('other_add_info_upload','upload',label='or'),

singular = 'Plant Growth Condition',plural = 'Growth') 


db.define_table('treatments',
    Field('sample_name','reference sample', writable = False),
#treatment factor start under treatments  1     -->23.3.13
    Field('treament_biotic_factor','string',label='Biotic'),
    Field('treatment_abiotic_factor','string',label='Abiotic'),
    Field('treatment_intervention','string',label='Intervention',comment='Description of treatment intervention methods such as agrochemicals, enzyme inhibitors, hormones, elicitors other factors'),
#treatment factor end under treatments    4     -->23.3.13
    Field('treatment_dose','string',label='Treatment Dose/Intensity levels'),
    Field('treatment_start_date','date',required=False,requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),maximum=datetime.date.today()))),
    Field('treatment_time_duration','string',label='Treament Time(Duration)'),
    Field('treatment_time','string'),
    Field('treatment_time_interval','string'),
    Field('treatment_description','text'),
    Field('treatment_before_harvest','string',label='Treatment duration before harvest'),
    Field('additional_information','text',label='Additional Information'),
    Field('other_add_info_upload','upload',label='or'),
singular = 'Treatments',plural = 'Treatments')
#2.4
#schema changes - additional comments field is added for harvest amount 

db.define_table('harvests',
    Field('sample_name','reference sample', writable = False),
    Field('harvest_date','date',label='Harvest Date(YYYY-MM-DD)',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),maximum=datetime.date.today()))),
    Field('harvest_time','time',label='Harvest Time(HH:MM:SS)',requires=IS_EMPTY_OR(IS_TIME())),
    Field('plant_growth_stage','string',label='plant growth stage/developmental stage',comment='Information about plant growth stage used for harvest'),
    Field('metalbolism_quenching_method','text',length=2000,comment='Quenching method applied to stop biological metabolism  (Example: Liquid nitrogen)'),
    Field('harvest_method','text'),
    Field('harvest_amount','string',label='Harvest Amount(in grams)',comment='Amount of plant material used for harvest'),
    Field('harvest_amount_comment','text'),
    Field('harvest_storage_location','string'),
#sample storage start under harvest     9     -->23.3.13
    Field('sample_storage_description','text',label='Storage Description'),
    Field('sample_storage_date','date',label='Storage Date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),maximum=datetime.date.today()))),
    Field('sample_storage_location','string',label='Storage location'),
    Field('sample_storage_temparature','string',label='Storage Temperature'),
#sample storage start under harvest     13     -->23.3.13
    Field('additional_information','text',label='Additional Information'),
    Field('other_add_info_upload','upload',label='or'),
singular= 'Harvest',plural='Harvests')


#seperate table for 2.6 to 2.7 since they are multivalued attributes for a sample


db.define_table('extraction_preparation',
		Field('sample_name','reference sample', writable = False),
		Field('sample_id','integer',notnull=True,required=True,requires=IS_INT_IN_RANGE(0,100000000,error_message='Enter a positive number')),
		Field('sample_extraction_date','date',required=False,requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),label='Date of sample Extraction'),
                Field('harvest_stage','string'),
                Field('amount_of_sample_taken','string'),
		Field('sample_extraction_desc','text',length=5000,label='Sample Processing and Extraction'),
		Field('extraction_solvent','text',length=1000),
		Field('extraction_protocol','text'),
                Field('extraction_protocol_name','text',label='Name of protocol/Method'),
		Field('extraction_volume','double',label='Extraction Volume (ml)',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,1000,error_message='too large !!')),comment='Total volume of extract'),
		Field('resuspension_process','text',length=5000,label='Extract Concentration and Resuspension Process',comment='Description of method applied for concentrating the extract (Example: Centrivap cold trap vacuum concentrator)'),
		Field('extract_cleanup','text',length=5000,label='Extract Clean-Up',comment='Clean-Up method used for remove additional salts and unwanted components'),
#extract storage under ep   10        -->23.3.13
                Field('storage_description','text',length=5000),
		Field('storage_location','text',length=1000),
		Field('storage_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
		Field('storage_temparature','double',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-400,400,error_message='from -400 to +400 in celsius')),label='Storage Temparature (in Celsius)'),
#extract storage end  under ep   14        -->23.3.13
		Field('preparation_protocol','text',length=8000,label='Sample Preparation Protocol Description'),
		Field('storage_condition','text',length=1000),
                Field('preparation_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
		Field('sample_extraction_times','integer',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,6))),
                Field('additional_information','text',label='Additional Information'),
                Field('other_add_info_upload','upload',label='or'),
singular='Extraction Preparation',plural='Extraction Preparation')



#3.1.1 GC
db.define_table('gas_chromatography',

#Sample extraction column start under gc  0   --->23.3.13  
    Field('sample_name','reference sample', writable = False),
    Field('sample_id','integer',notnull=True,required=True,requires=IS_INT_IN_RANGE(0,100000000,error_message='Enter a positive number')),
    Field('sample_extraction_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),label='Date of sample Extraction'),
    Field('harvest_stage','string'),
    Field('amount_of_sample_taken','string'),
    Field('sample_extraction_desc','text',length=5000,label='Sample Processing and Extraction'),
    Field('extraction_solvent','text',length=1000),
    Field('extraction_protocol','text'),
    Field('name_of_protocol','string',label='Name of Protocol/Method'),
    Field('extraction_volume','double',label='Extraction Volume (ml)',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,1000,error_message='too large !!'))),
    Field('resuspension_process','text',length=5000,label='Extract Concentration and Resuspension Process'),
    Field('extract_cleanup','text',length=5000,label='Extract Clean-Up'),

#extract storage start under gc     12    -->23.3.13
    Field('storage_description','text',length=5000),
    Field('storage_location','text',length=1000),
    Field('storage_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_temparature','double',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-400,400,error_message='from -400 to +400 in celsius')),label='Storage Temparature (in Celsius)'),
#extract storage end under gc     16    -->23.3.13
#Sample extraction column end under gc  16   --->23.3.13  

#sample preparation start under gc   16   ---->23.3.13
    Field('preparation_protocol','text',length=8000,label='Sample Preparation Protocol Description'),
    Field('preparation_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_condition','text',length=1000),
    Field('dat_of_storage','date',label='Date of Storage',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('sample_extraction_times','integer',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,6))),
#sample preparation end under gc   21   ---->23.3.13
#GC
#chromatography instrumental start under gc  21   --->23.3.13  
    Field('instrument_manufacturer','string',label='Manufacturer'),
    Field('instrument_model_name','string',label='Model name/number'),
    Field('instrument_software_package','string',label='Software package'),
    Field('instrument_version_number_or_date','string',label='Version number or Date'),
#chromatography instrumental end under gc  25   --->23.3.13  

#Derivatization start under gc  25   --->23.3.13  
#3.1.2 GC
    Field('derivatization_method','string',label='Method'),
    Field('reagents_used_for_derivation','string',label='Reagents used for Derivatization'),
    Field('derivatization_temperature','string',label='Derivatization temperature (in degree centigrade)'),
    Field('derivatization_duration','string',label='Duration(in min)'),
    Field('sample_phase','string',requires=IS_EMPTY_OR(IS_IN_SET(['polar','non-polar']))),
#Derivatization end under gc  30   --->23.3.13  
#3.1.3
#Auto injector start under gc  30   --->23.3.13  
    Field('injector_model','string',label='Injector model/type',comment='Injection system used'),
    Field('injector_software_version','string',label='Software version'),
    Field('method_name','text',label='Method name (used for sample injection)'),
    Field('injection_volume','string'),
    Field('wash_cycles','string',label='Wash cycles(volumes)',comment='Number of cycles applied for injector wash and volume used'),
    Field('solvent','string'),
    Field('sample_size','string',label='Sample size/concentration'),
#Auto injector end under gc  37   --->23.3.13  
#3.1.41
#Seperation column start under gc  37   --->23.3.13  
    Field('column_manufacturer','string',label='Manufacturer'),
    Field('product_name_and_catalogue_number_of_column','string',label='Product Name and catalogue number (year of catalogue)'),
    Field('stationary_media_composition','string',requires=IS_NOT_EMPTY()),
    Field('internal_diameter_of_column','string'),
    Field('length_of_column','string'),
    Field('column_temperature_program','text'),
    Field('column_head_pressure','string',label='Column head pressure(in psi)'),
    Field('flow_rate','double',label='Flow rate(in mL/min)'),
#Seperation column end under gc  45   --->23.3.13  
#Seperation parameters column start under gc  45   --->23.3.13  
#3.1.5
    Field('seperation_method_name','string',label='Method name'),
    Field('injector_temperature','string',label='Injector tempreature(in degree*c)'),
    Field('split_splitless_mode','string',requires=IS_EMPTY_OR(IS_IN_SET({'0':'Split mode','1':'Splitless mode'})),label='Split or splitless mode',comment='The carrier gas either sweeps the entirety (splitless mode) or a portion (split mode) of the sample into the column'),
    Field('split_ratio','string',comment='Split vent flow rate/column flow rate'),
    Field('mobile_phase_composition','text'),
    Field('mobile_phase_flow_rate','double',label='Mobile phase flow rate(in ml/min)'),
    Field('thermal_gradient_profiles','text',length='1000'),
#Seperation parameters column end under gc  52   --->23.3.13  

#3.1.6
#Quality control column start under gc  52   --->23.3.13  
    Field('validation_sample','string'),
    Field('internal_standards','string'),
    Field('external_standards','string'),
    Field('chromatographic_resolution','string'),
#Cycles column start under gc  56   --->23.3.13  
    Field('cycle_per_column','integer'),
    Field('cycle_per_injector','integer'),
    Field('cycle_per_septum','string'),
    Field('cycle_per_blank','integer'),
    Field('detector','string'),
#Cycles column end under gc  61   --->23.3.13  
#Quality control end under gc  61   --->23.3.13  
#3.1.7
#Acqusation column start under gc  61   --->23.3.13  
    Field('SOP_protocol_name','string'),
    Field('date_of_analysis','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('operator','reference auth_user'),
    Field('tergetted_or_untargtted_approach',requires=IS_EMPTY_OR(IS_IN_SET({'0':'Targetted Approach','1':'Untargetted Approach'})),label='Approach'),
    Field('deviation_from_SOP','text',length=1000),
    Field('publication_refernce','text',length=1000,label='Publication reference(If any)'),
    Field('additional_information','text',label='Additional Information'),
    Field('other_add_info_upload','upload',label='or'),
plural='GC')
#Acqusation column end under gc  69   --->23.3.13  

#LC
db.define_table('liquid_chromatography',
#Sample extraction column start under lc  0   --->23.3.13  
    Field('sample_name','reference sample', writable = False),
    Field('sample_id','integer',notnull=True,required=True,requires=IS_INT_IN_RANGE(0,100000000,error_message='Enter a positive number')),
    Field('sample_extraction_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),label='Date of sample Extraction'),
    Field('harvest_stage','string'),
    Field('amount_of_sample_taken','string'),
    Field('sample_extraction_desc','text',length=5000,label='Sample Processing and Extraction'),
    Field('extraction_solvent','text',length=1000),
    Field('extraction_protocol','text'),
    Field('name_of_protocol','string',label='Name of Protocol/Method'),
    Field('extraction_volume','double',label='Extraction Volume (ml)',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,1000,error_message='too large !!'))),
    Field('resuspension_process','text',length=5000,label='Extract Concentration and Resuspension Process'),
    Field('extract_cleanup','text',length=5000,label='Extract Clean-Up'),
# extraction storage column start under lc  12   --->23.3.13  
    Field('storage_description','text',length=5000),
    Field('storage_location','text',length=1000),
    Field('storage_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_temparature','double',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-400,400,error_message='from -400 to +400 in celsius')),label='Storage Temparature (in Celsius)'),
# extraction storage column end under lc  16   --->23.3.13  
#Sample extraction column end under lc  16   --->23.3.13  
# sample preparation column start under lc  16   --->23.3.13  
    Field('preparation_protocol','text',length=8000,label='Sample Preparation Protocol Description'),
    Field('preparation_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_condition','text',length=1000),
    Field('date_of_storage','date',label="Date of Storage",requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('sample_extraction_times','integer',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,6))),
# sample preparation column end under lc  21   --->23.3.13  
#LC   21  chromatography instrumental
    Field('instrument_manufacturer','string',label='Manufacturer'),
    Field('instrument_model_name_ornumber','string',label='Model name/number'),
    Field('instrument_software_package','string',label='Software package'),
    Field('instrument_version_number_or_date','string',label='Version number or Date'),
#3.1.3   25 
#  25  chromatography instrumental end
#  auto injector   start  25
    Field('injector_model','string',label='Injector model/type',comment='Injection system used'),
    Field('injector_software_version','string',label='Software version'),
    Field('method_name','text',label='Method name (used for sample injection)'),
    Field('injection_volume','string'),
    Field('wash_cycles','string',label='Wash cycles(volumes)',comment='Number of cycles applied for injector wash and volume used'),
    Field('solvent','string'),
    Field('sample_size_or_concentration',label='Sample size/concentration'),
#  auto injector   end 32
#3.1.41 seperation column start
    Field('column_manufacturer','string',label='Manufacturer'),
    Field('product_name_and_catalogue_number_of_column','string',label='Product Name and catalogue number (year of catalogue)'),
    Field('stationary_media_composition','string'),
    Field('internal_diameter_of_column','string'),
    Field('length_of_column','text'),
    Field('column_temperature_program','text'),
    Field('column_head_pressure','double',label='Column head pressure(in psi)'),
    Field('flow_rate','double',label='Flow rate(in mL/min)'),
#3.1.41 seperation column end  40
#3.1.5seperation parameters 40
    Field('seperation_method_name','string',label='Method name'),
    Field('injector_temperature','string',label='Injector tempreature(in degree*c)'),
    Field('split_splitless_mode','string',requires=IS_EMPTY_OR(IS_IN_SET(['Split mode','Splitless mode'])),label='Split or splitless mode',comment='The carrier gas either sweeps the entirety (splitless mode) or a portion (split mode) of the sample into the column'),
    Field('split_ratio','string',comment='Split vent flow rate/column flow rate'),
    Field('mobile_phase_composition','text'),
    Field('mobile_phase_flow_rate','double',label='Mobile phase flow rate(in ml/min)'),
    Field('solvent_gradient_profiles','text',length='1000'),
#3.1.41 seperation parameters end  47
#3.1.6  quality control start 47
    Field('validation_sample','string'),
    Field('internal_standards','string'),
    Field('external_standards','string'),
    Field('chromatographic_resolution','string'),
#3.1.6 cycles start  51
    Field('cycle_per_column','integer'),
    Field('cycle_per_injector','integer'),
    Field('cycle_per_septum','string'),
    Field('cycle_per_blank','integer'),
#cycles end at 55
    Field('detector','string'),
#quality control end at 56
#3.1.7 data acqusation at 56
    Field('SOP_protocol_name','string'),
    Field('date_of_analysis','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('operator','reference auth_user'),
    Field('deviation_from_SOP','text',length=1000),
    Field('tergetted_or_untargtted_approach',requires=IS_EMPTY_OR(IS_IN_SET({'0':'Targetted Approach','1':'Untargetted Approach'})),label='Approach'),
    Field('publication_refernce','text',length=1000,label='Publication reference'), Field('additional_information','text',label='Additional Information'),
    Field('other_add_info_upload','upload',label='or'),
  # 64

plural='LC')

# main table for  3.2 
db.define_table('mass_spectroscopy',

     Field('sample_name','reference sample', writable = False),
# table 3.2.1 instrumental details under ms 1
     Field('manufacturer','string',),    
     Field('model','string',),    
     Field('oper_soft_name','string',label='operational software name ',),    
     Field('oper_soft_ver','string',label='operational software version',),   
# table 3.2.1 instrumental details under ms 5

# table 3.2.2 ionization soource start 5
     Field('ionization_mode','string',required=False),    
     Field('polarity','string',required=False,comment='Capillary voltage +ve or –ve charge produced after ionization on which analysis should be performed'),    
     Field('vaccum_pressure','string'),    
     Field('len_voltages','string',label=' skimmer/focusing lens voltages '),    
     Field('gas_flows','string',comment='Flow rate and the name of gas used in the ionizer for the flow of ions.  e.g. nebulization gas, cone gas etc.'),    
     Field('sour_temp','string',label='source temperature'),    

      
# table 3.2.2 ionisation source under ms 11
# table 3.2.3 mass analyzer 11
     Field('type_of_analyzer','string'),    
     Field('m_range','string',label='m/z_range'),    
     Field('calibration_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),    
     Field('resolution1','string',label='Resolution'),    
     Field('mass_accuracy1','string',label='Mass accuracy'),    
     Field('log_program','string',label='Logic program for data acquistion',comment='Logic control system used for data acquisition'),    
     Field('spectral_acquisition_rate','string'),    
     Field('vaccum_pressure','string'),    
# lock spray under Mass analyzer 19
     Field('concentration','string'),    
     Field('lock_mass','string',comment='Electrospray ion source details the co-introduction of analyte and lock mass compound directly into the ion source, to provide authenticated exact mass measurement'),    
     Field('flow_rate','string'),    
     Field('frequency','string'),    
# lock spray end under Mass analyzer 23
     Field('add_info','text',label='additional information '),

#  Mass analyzer end under 24

# table 3.2.4 quality control 24
     Field('tune','string',comment='Autotune or manual tune (Time at which the machine’s attributes are adjusted according to the experiment)'),
     Field('sensitivity','string'),
     Field('mass_accuracy2','string',label='mass accuracy'),
     Field('resolution2','string',label='Resolution'),
     Field('detector','string',label='Detector'),

# quality control end at 29
      
# table 3.2.5 acquisation at 29
     Field('SOP_protocol','text'),
     Field('date_of_data_acquistion','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
     Field('operator','string'),
     Field('data_acquisition_rate','string'),
     
     Field('deviation_from_SOP','string'),

     Field('replicate_sample_analysis','integer'),
     Field('additional_information','text',label='Additional information '),
     Field('other_add_info_upload','upload',label='or'),
 #37
  
     plural='MS')


db.define_table('spectrophotometry',

# table 3.2.1
     Field('sample_name','reference sample', writable = False),
     Field('wavelength','string'),
     Field('optical_density','string'),
     Field('Final_concentration_of_compound','string'),plural='SPM')

db.define_table('raw_data_storage_information',
    Field('sample_name','reference sample',writable=False),
  #  Field('email_id_of_person','string',label='Email id',required=True,requires=IS_EMAIL()),
  #  Field('identification_of_metabolites','text',label='Identification Of Metabolites'),
  #  Field('no_of_perks','integer',label='Number of Peaks'),
  #  Field('no_of_peaks_unidentified','integer',label='Number of Unidentified Peaks'),
  #  Field('number_of_metabolites','integer',label='Number Of Metabolites'),
  #  Field('referred_library','string',label='Referred Library and Version'), 
    Field('raw_data_file_name','string',label='Raw data file name'),
    Field('raw_data_file_upload','upload',label='Raw data file'),
    Field('raw_data_standard_format','string',label='Raw data standard format file name'),
    Field('raw_data_standard_format_upload','upload',label='Converted standard data file'),
    
    Field('additional_information_about_data','text',label='Additional information about data files'),
    Field('additional_information_upload','upload',label='Additional data file'),
   # Field('date_of_data_upload','date',label='Date of data uploaded',requires=IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())
    plural='RDS')



db.define_table('feedback',
               Field('feedback_on',required=True),
               Field('feedback_body','text',required=True,requires=IS_NOT_EMPTY()),
               Field('feedback_by','reference auth_user',notnull=False))                                                              




db.define_table('sample_files',
		Field('sample','reference sample',readable=False,writable=False),
		Field('file_name',requires=IS_NOT_EMPTY(),readable=False,writable=False),
		Field('file','upload',label='Additional Sample Data',required=True,notnull=True,autodelete=True,requires=IS_NOT_EMPTY()),
		Field('user','reference auth_user',readable=False,writable=False),
		Field('description','text',requires=IS_NOT_EMPTY()),format='%(sample)s')


def name(identifier):
   ans = db(db.auth_user.id == identifier).select().first()
   f = str(ans.first_name)+' '+str(ans.last_name)
   return f



#defines task,who did it, when did they push it and when it got compelted, task parameters, etc

db.define_table('task',
		Field('user','reference auth_user',readable=False,writable=False),
		Field('status','string',requires=IS_IN_SET({0:'QUEUED',1:'RUNNING',2:'COMPLETED',3:'FAILED'},zero=None),readable=False,writable=False),
		Field('start_time','datetime',requires=IS_DATETIME(format='%d-%m-%Y %H:%M:%S'),readable=False,writable=False),
		Field('end_time','datetime',readable=False,writable=False,requires=IS_EMPTY_OR(IS_DATETIME(format='%d-%m-%Y %H:%M:%S'))),
		Field('peak_detection_method',notnull=True,required=True,requires=IS_IN_SET({0:'Cent Wave',1:'Matched Filter'},zero=None)),
		Field('ppm','double',default=2.5,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(2.5,100,error_message='should be between 2.5 and 100')]),
		Field('min_peak_width','double',default=0.6,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(0.6,10,error_message='should be between 0.6 and 10')]),
		Field('max_peak_width','double',default=1.4,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(1.4,60,error_message='should be between 1.4 and 60')]),
		
		Field('step_size','double',default=0.1,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(0.1,0.5,error_message='should be between 0.1 and 0.5')]),
		Field('fwhm','double',default=3,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(3,30,error_message='should be between 3 and 30')]),
		Field('alignment_method',notnull=True,required=True,requires=IS_IN_SET({0:'Density',1:'mzClust',2:'Nearest'},zero=None)),
		Field('mzwid','double',default=0.015,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(0.015,0.25,error_message='should be between 0.015 and 0.25')]),
		Field('minfrac','double',default=0.1,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(0.1,0.5,error_message='should be between 0.1 and 0.5')]),
		Field('bw','double',default=3,required=True,requires=[IS_NOT_EMPTY(),IS_FLOAT_IN_RANGE(3,30,error_message='should be between 3 and 30')]),
		Field('retention_time_method',notnull=True,required=True,requires=IS_IN_SET({0:'Peak Groups',1:'Obiwarp'},zero=None)),
		Field('peak_groups_method',notnull=True,required=True,requires=IS_IN_SET({0:'LOESS',1:'Linear'},zero=None)))
		
		
db.define_table('nmr_attributes',
    Field('sample_name','reference sample', writable = False),
    
#NMR ATTRIBUTES FOR SAMPLE DATA
    # NMR sample
    Field('original_biological_sample_reference','string',label='Original biological sample reference'), #1
    Field('original_biological_sample','double',label='Original biological sample Ph'),
    Field('post_buffer_ph','double',label='Post buffer Ph'),
    Field('concentration_of_solute_in_sample','double',label='Concentration of solute in sample'),
    Field('concentration_of_chemical_shift_std_in_sample','double',label='Concentration of chemical shift Std in sample'),
    Field('concentration_of_solvent_in_sample_standard_within_the_sample','double',label='Concentration of solvent in sample standard within the sample'),
    Field('concentration_of_concentration_Std_in_sample','double',label='Concentration of concentration Std in sample'), #7
    Field('concentration_std_type','string',label='Concentration std type'),
    Field('field_frequency_lock_name','string',label='Field frequency lock name'),
    Field('additional_solute_name','string',label='Additional solute name'),
    Field('chemical_shift_std_name','string',label='Chemical shift std name'),
    Field('solvent_name','string',label='Solvent name'),
    Field('concentration_std_name','string',label='Concentration std name'), #13

#NMR ATTRIBUTES FOR INSTRUMENT
    Field('location','string',label='Location'), #14
    #Magnet
    Field('magnet_serial_no','string',label='Serial No.'), #15
    Field('magnet_manufacturer','string',label='Manufacturer'),
    Field('magnet_model','string',label='Model'),
    Field('magnet_field_strength','double',label='Field strength'), #18
    #Probe
    Field('probe_serial_no','string',label='Serial No.'), #19
    Field('probe_manufacturer','string',label='Manufacturer'),
    Field('probe_model','string',label='Model'),
    Field('probe_gradient_strength','double',label='Gradient strength'), #22
    #Console
    Field('console_serial_no','string',label='Serial No.'), #23
    Field('console_manufacturer','string',label='Manufacturer'),
    Field('console_model','string',label='Model'), #25
    #Acquisition computer
    Field('acquisition_computer_serial_no','string',label='Serial No.'), #26
    Field('acquisition_computer_manufacturer','string',label='Manufacturer'),
    Field('acquisition_computer_model','string',label='Model'),
    Field('acquisition_computer_operating_system_software','string',label='Operating system software '),
    Field('acquisition_computer_operating_system_version','string',label='Operating system version'),
    Field('acquisition_computer_application_software','string',label='Application software'),
    Field('acquisition_computer_application_software_version','string',label='Application software version'), #32
    #Autosampler
    Field('autosampler_serial_no','string',label='Serial No.'), #33
    Field('autosampler_manufacturer','string',label='Manufacturer'),
    Field('autosampler_model','string',label='Model'),
    Field('autosampler_application_software','string',label='Application software'),
    Field('autosampler_application_software_version','string',label='Application software version'), #37
#INSTRUMENT ACQUISITION PARAMETERS
    #Acquisition parameter set
    Field('acquisition_params_file_ref','string',label='Acquisition params file ref'), #38
    Field('sample_introduction_method','string',label='Sample introduction method'),
    Field('sample_introduction_method_size','double',label='Sample introduction method size'),
    Field('sample_temperature_in_auto_sampler','double',label='Sample temperature in auto sampler'),
    Field('sample_temperature_in_magnet','double',label='Sample temperature in magnet'),
    Field('spinning_rate','string',label='Spinning rate'),
    Field('water_suppression','string',label='Water suppression'),
    Field('pulse_sequence','string',label='Pulse sequence'),
    Field('pulse_sequence_file_ref','string',label='Pulse sequence file ref'),
    Field('pulse_sequence_literature_ref','string',label='Pulse sequence literature ref'),
    Field('number_of_steady_state_scans','string',label='Number of steady state scans'),
    Field('number_of_scans','string',label='Number of scans'),
    Field('relaxation_delay','string',label='Relaxation delay'), #50
    #Acquisition parameters recorded for each dimension
    Field('irradiation_frequency','double',label='Irradiation frequency'), #51
    Field('acquisition_nucleus','string',label='Acquisition nucleus'),
    Field('deg_90_pulse_width','double',label='Deg 90 pulse width'),
    Field('dwell_time','double',label='Dwell time'),
    Field('no_of_data_points','string',label='No of data points'), #55
    #Acquisition parameters recorded for second and higher dimensions
    Field('encoding','string',label='Encoding'), #56
    Field('shaped_pulse_file_ref','string',label='Shaped pulse file ref.'),
    Field('hadamard_frequency','double',label='Hadamard frequency'), #58
#QUALITY CONTROL
    Field('signal','string',label='Signal'), #59
    Field('line_width','double',label='Line width'),
    Field('peak_width_at_5_percent_intensity','double',label='Peak width at 5 Percent Intensity'), #61
#NMR ATTRIBUTES FOR DATA PROCESSING
    #FID & Spectral Processing Parameter Set
    Field('post_acquisition_water_suppression','string',label='Post Acquisition Water Suppression'), #62
    Field('transformation_type','string',label='Transformation Type'),
    Field('calibration_compound','string',label='Calibration Compound'), #64
    #Processing Parameters Recorded for Each Dimension
    Field('processing_params_file_ref','string',label='Processing Params File Ref'), #65
    Field('no_of_data_points_in_spectrum','string',label='No Of Data Points In Spectrum'),
    Field('zero_order_phase_correction','double',label='Zero Order Phase Correction'),
    Field('first_order_phase_correction','double',label='First Order Phase Correction'),
    Field('calibration_reference_shift','double',label='Calibration Reference Shift'),
    Field('baseline_correction','string',label='Baseline Correction'),
    Field('spectral_denoising','string',label='Spectral De-noising'), #71
    #Window function parameters
    Field('window_function','string',label='Window Function'), #72
    #Parameter to window function parameters
    Field('window_function_parameter','string',label='Window Function Parameter'), #73
    Field('parameter_value','string',label='Parameter Value'), #74
    #2D J-Resolved processing parameters
    Field('rotate45_deg','string',label='rotate45 Deg'), #75
    Field('symmetrize','string',label='Symmetrize'), #76
    #Processing software parameters
    Field('software','string',label='Software'), #77
    Field('software_version','string',label='Software Version'),
    Field('projection_method','string',label='Projection Method'),
    Field('projection_axis','string',label='Projection Axis'), #80
    #Spectral quantitation data set
    Field('spectral_quantitation_type','string',label='Spectral Quantitation Type'), #81
    Field('spectral_quantitation_algorithm','string',label='Spectral Quantitation Algorithm'),
    Field('spectral_quantitation_parameters','string',label='Spectral Quantitation Parameters'),
    Field('manual_spectral_quantitation','string',label='Manual Spectral Quantitation'), #84
#ATTRIBUTES FOR DATA SETS
    #1D_FID_Data_Set
    Field('oned_fid_data_set_x_axis_Units','double',label='X Axis Units'), #85
    Field('oned_fid_data_set_y_axis_Units','double',label='Y Axis Units'),
    Field('oned_fid_data_set_x_start_value','double',label='X Start Value'),
    Field('oned_fid_data_set_X_end_Value','double',label='X End Value'),
    Field('oned_fid_data_set_number_of_data_points','double',label='Number of Data Points'),
    Field('oned_fid_data_set_data_matrix','string',label='data_matrix'), #90
    #FID_File_Reference
    Field('Fid_File_ref','string',label='Fid File Ref'), #91
    #2D_FID_Data_Set
    Field('twod_fid_data_set_additional_axis_units','double',label='Additional Axis Units'), #92
    Field('twod_fid_data_set_x_axis_units','double',label='X Axis Units'),
    Field('twod_fid_data_set_y_Axis_units','double',label='Y Axis Units'),
    Field('twod_fid_data_set_x_Start_value','double',label='X Start Value'),
    Field('twod_fid_data_set_x_End_value','double',label='X End Value'),
    Field('twod_fid_data_set_Number_of_Data_Points','double',label='Number of Data Points'),
    Field('twod_fid_data_set_data_matrix','string',label='data_matrix'), #98
    #1D_spectrum
    Field('oned_spectrum_x_axis_units','double',label='X Axis Units'), #99
    Field('oned_spectrum_y_axis_units','double',label='Y Axis Units'),
    Field('oned_spectrum_x_start_value','double',label='X Start Value'),
    Field('oned_spectrum_x_end_value','double',label='X End Value'),
    Field('oned_spectrum_number_of_data_points','double',label='Number of Data Points'),
    Field('oned_spectrum_data_matrix','string',label='data_matrix'), #104
    #2D_spectrum
    Field('twod_spectrum_additional_axis_units','double',label='Additional Axis Units'), #105
    Field('twod_spectrum_x_axis_units','double',label='X Axis Units'),
    Field('twod_spectrum_y_axis_units','double',label='Y Axis Units'),
    Field('twod_spectrum_x_start_value','double',label='X Start Value'),
    Field('twod_spectrum_x_end_value','double',label='X End Value'),
    Field('twod_spectrum_number_of_data_points','double',label='Number of Data Points'),
    Field('twod_spectrum_data_matrix','string',label='data_matrix'), #111
    #2D_Projected_Spectrum
    Field('twod_projected_spectruem_x_axis_units','double',label='X Axis Units'), #112
    Field('twod_projected_spectruem_y_axis_units','double',label='Y Axis Units'),
    Field('twod_projected_spectruem_x_start_value','double',label='X Start Value'),
    Field('twod_projected_spectruem_x_end_value','double',label='X End Value'),
    Field('twod_projected_spectruem_number_of_data_points','double',label='Number of Data Points'),
    Field('twod_projected_spectruem_data_matrix','string',label='data_matrix'), #117
    #Bucketed_Spectrum
    Field('bucketed_spectrum_x_axis_units','double',label='X Axis Units'), #118
    Field('bucketed_spectrum_y_axis_units','double',label='Y Axis Units'),
    Field('bucketed_spectrum_number_of_data_points','double',label='Number of Data Points'),
    Field('bucketed_spectrum_data_matrix','string',label='data_matrix'), #121
    #Peak-picked_Spectrum
    Field('peak_picked_spectrum_x_axis_units','double',label='X Axis Units'), #122
    Field('peak_picked_spectrum_y_axis_units','double',label='Y Axis Units'),
    Field('peak_picked_spectrum_number_of_data_points','double',label='Number of Data Points'),
    Field('peak_picked_spectrum_data_matrix','string',label='data_matrix'), #125

singular = 'NMR sample',plural = 'NMR samples')


## Module 2
## Tables for jobs, scheduler, methods etc.

#instrument table
db.define_table('instrument',
    Field('method1','string'),
    Field('method2','string'),
    Field('method3','string'))

#default instruments table
db.define_table('default_instrument',
    Field('instrument_id',db.instrument),
    Field('name','string'))

#centwave method table
db.define_table('centwave',
    Field('instrument_id',db.instrument, writable=False, readable=False),
    Field('ppm','double'),
    Field('min_peak_width','double'),
    Field('max_peak_width','double'))


#matched Filter method table
db.define_table('matchedfilter',
    Field('instrument_id',db.instrument, writable=False, readable=False),
    Field('fwhm','double'),
    Field('step','double'))

#density method table
db.define_table('density',
	Field('instrument_id',db.instrument, writable=False, readable=False),
    Field('mzwid','double'),
    Field('minfrac','double'),
    Field('bw','double')
    
    )
#MzClust method table
db.define_table('mzclust',
    Field('instrument_id',db.instrument, writable=False, readable=False)
    )

#nearest method table
db.define_table('nearest',
    Field('instrument_id',db.instrument, writable=False, readable=False)
    )

#obiwarp method table
db.define_table('obiwarp',
    Field('instrument_id',db.instrument, writable=False, readable=False)
    )

#peakgroup method table
db.define_table('peakgroup',
    Field('instrument_id',db.instrument, writable=False, readable=False),
    Field('smooth','string')
    )

#job table
db.define_table('job',
    Field('id','reference auth_user'),
    Field('instrument_id',db.instrument),
    Field('id','reference scheduler_task'))
