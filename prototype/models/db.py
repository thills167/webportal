#s scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
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
     Field('project_publication_date','date',writable=False,readable=False,required=False),
     
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
    Field('experiment','reference experiment',writable=False),
    Field('working_status',default=1,required=True,requires=IS_IN_SET({'0':'Completed','1':'In Progress'})),
    Field('replica',default='Original',required=True,requires=IS_IN_SET(['Original','replicate','aliquot']),label='Type'),
    Field('publication_status','boolean',default=False,required=True,label='Pub?'),format='%(name)s',singular='Sample',plural='Samples')


db.define_table('template',
    Field('user',unique=True,),
    Field('sample','reference sample'))

db.define_table('experiment',
    Field('experimentalist','reference auth_user'),
   # Field('analyst','reference auth_user'),
    Field('name',unique=True,notnull=True,required=True,label='Experiemnt Name'),
    Field('code',required=True,requires=IS_NOT_IN_DB(db,'experiment.code'),label='Experiment Code'),
    Field('description','text',length=2000,notnull=True,required=True,label='experiment Description'),
    Field('project','reference project',writable=False),
    Field('working_status',default=1,required=True,requires=IS_IN_SET({'0':'Completed','1':'In Progress'})),
    Field('publication_status','boolean',default=False,required=True,label='Published'),format='%(name)s',singular='experiment/group',plural='Experiments/Groups')

db.define_table('project_meta',
   Field('project','reference project'),
   Field('enitity','reference entity'))

#bio tables

#schema changes - plant_type (Inbred,Hybrid,Complete) is added 

# 2.1 
db.define_table('biosource',
    Field('sample_name','reference sample',writable = False),
    Field('species_name','string',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('genotype_echotype','string',label='Echotype/Background',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('phenotype','string',label='Phenotype'),
    Field('plant_type','string',requires=IS_IN_SET({'0':'Inbred','1':'Hybrid','2':'Composite'}),label='Plant Genetic Type'),
    Field('Source_of_germplasm','string',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('genotype_pedigree_information','string',label='Pedigree Information',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('genotype_plant_type','string',label='Plant Type',required=True,notnull=True,requires=IS_IN_SET({'Transgenic Type','Mutant Type','Wild Type'})),
    Field('genotype_gene_names','string',label='Gene Name(s)',required=True,notnull=True),
#Field('geno_gene_name',)
    
    Field('organ' ,'string',required=True,notnull=True,requires=IS_NOT_EMPTY()),
    Field('organ_spec','string',label='Organ Specification',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='Name or description of specific part of organ if any used for the study'),
    Field('cell_type','string',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment = 'Specific plant cells used after dissection or cell sorting or any other method. This naming should be used based on Plant Ontology Consortium (POC)'),
    Field('sub_cell_location','string',label='Sub Cellular Location',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='This is about sub cellular locations from cells are collected for experiment. Naming should be maintained based on Gene Ontology Cellular Component'),
    Field('bio_source_amount','string',label='BioSource Amount',required=True,notnull=True,requires=IS_NOT_EMPTY(),comment='This is reference to the mass (mg fresh weight or mg dry weight), number of cells or other measurable quantification information'))



#schema changes - date est other has been changed from date to text and the label has been changed

db.define_table('plant_growth_condition',
    Field('sample_name','reference sample', writable = False),
    Field('growth_soil','string',label='Soil (type, supplier)',),		
    Field('growth_agar','string',label='Agar (type, supplier)',),		
    Field('growth_vermiculite','string',label='Vermiculite (type, supplier)',),		
    Field('growth_hydroponic','string',label='Hydroponic system (type,supplier,nutrient concentrations)',),		
    Field('growth_cell_culture','string',label='Cell culture (media, volume,cell number per volume)',),
    Field('loc_field_location','string',label='Location',),	
    Field('loc_field_avr_humidity','string',label='Average Humidity',),
    Field('loc_field_avr_temp','string',label='Average Temperature',),
    Field('loc_field_avr_rain','string',label='Average Rain Fall',),
    Field('season','string'),
    Field('Climate_chamber_size','string',label='Climate chamber size (m3)',),
    Field('Climate_chamber_co2_concentration','string'),
    Field('loc_green_location','string',label='Location',),		
    Field('loc_green_light','string',label='Light (quality,source mode/type,intensity, luminescence period(hr.),dark period (hr.))',),		
    Field('loc_green_humidity','string',label='Humidity (day,night)',),
    Field('loc_green_temperature','string',label='Temperature (day,night)',),		
    Field('loc_green_water','string',label='Water Regime (Amount, time per day) ',),
    Field('Growth_Protocol_Description','text',label='Growth Protocol Description'),	
    Field('growth_protocol_description_upload','upload',label='or'),	
    Field('Growth_Plot_Design','text',label='Growth Plot Design',),		
    Field('nutr_amount','string',label='Nutrient Amount',),		
    Field('nutr_duration','string',label='Duration',),		
    Field('nutr_add_info','text',label='Additional information',),
    Field('sowing_period','string'),
#,required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!',))),		
    Field('gerrminating_period','string'),
#,label='Date of Germination',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),
    Field('date_est_transplanting','string'),
#,label='Date of Transplanting',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),
    Field('date_est_cutting','string'),
#,label='Date of cutting',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),		
    Field('date_est_grafting','string'),
    Field('hydroponic_type','string'),
    Field('hydroponic_supplier','string'),
    Field('hydroponic_nutrient_concentration','string'),
    Field('hydroponic_volume','string'),
    Field('hydroponic_number_of_plats','string',label='No. of plats/tray or container'),
    Field('hydroponic_frequency','string',label='frequency of nutrient changed'),
    Field('hydroponic_aeration_provided','boolean'),
    
#,label='Date of Grafting ',required=False,requires=IS_EMPTY_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='must be YYYY-MM-DD!'))),	
    Field('date_est_other','string',label='Additional Information (Stages etc)',required=False),	
    Field('other_spec','string',label='Other Specific Metadata'),	
    Field('other_spec_upload','upload',label='or'),singular = 'Plant Growth Condition',plural = 'Growth'
    ) 


db.define_table('treatments',
    Field('sample_name','reference sample', writable = False),
    Field('treament_biotic_factor','string',label='Biotic'),
    Field('treatment_abiotic_factor','string',label='Abiotic'),
    Field('treatment_intervention','string',label='Intervention'),
    Field('treatment_dose','string',label='Treatment Dose/Intensity levels'),
    Field('treatment_start_date','date',required=False,requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),maximum=datetime.date.today()))),
    Field('treatment_time_duration','string',label='Treament Time(Duration)'),
    Field('treatment_time','string'),
    Field('treatment_time_interval','string'),
    Field('treatment_description','text'),
    Field('treatment_before_harvest','string',label='Treatment duration before harvest'),singular = 'Treatments',plural = 'Treatments')
#2.4
#schema changes - additional comments field is added for harvest amount 

db.define_table('harvests',
    Field('sample_name','reference sample', writable = False),
    Field('harvest_date','date',label='Harvest Date(YYYY-MM-DD)',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),maximum=datetime.date.today()))),
    Field('harvest_time','time',label='Harvest Time(HH:MM:SS)',requires=IS_EMPTY_OR(IS_TIME())),
    Field('plant_growth_stage','string',label='plant growth stage/developmental stage'),
    Field('metalbolism_quenching_method','text',length=2000),
    Field('harvest_method','text'),
    Field('harvest_amount','string',label='Harvest Amount(in grams)'),
    Field('harvest_amount_comment','text'),
    Field('harvest_storage_location','string'),
    Field('sample_storage_description','text',label='Storage Description'),
    Field('sample_storage_date','date',label='Storage Date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),maximum=datetime.date.today()))),
    Field('sample_storage_location','string',label='Storage location'),
    Field('sample_storage_temparature','string',label='Storage Temperature'),singular= 'Harvest',plural='Harvests')


#seperate table for 2.6 to 2.7 since they are multivalued attributes for a sample


db.define_table('extraction_preparation',
		Field('sample_name','reference sample', writable = False),
		Field('sample_id','integer',notnull=True,required=True,requires=IS_INT_IN_RANGE(0,100000000,error_message='Enter a positive number')),
                Field('harvest_stage','string'),
		Field('sample_extraction_date','date',required=False,requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),label='Date of sample Extraction'),
                Field('amount_of_sample_taken','string'),
		Field('sample_extraction_desc','text',length=5000,label='Sample Processing and Extraction'),
		Field('extraction_solvent','text',length=1000),
		Field('extraction_protocol','text'),
                Field('extraction_protocol_name','text',label='name of protocol/Method'),
		Field('extraction_volume','double',label='Extraction Volume (ml)',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,1000,error_message='too large !!'))),
		Field('resuspension_process','text',length=5000,label='Extract Concentration and Resuspension Process'),
		Field('extract_cleanup','text',length=5000,label='Extract Clean-Up'),
    Field('plant_type','string',requires=IS_IN_SET({'0':'Inbred','1':'Hybrid','2':'Composite'}),label='Plant Genetic Type'),
    Field('Source_of_germplasm','string',required=True,notnull=True,requires=IS_NOT_EMPTY()),
                Field('storage_description','text',length=5000),
		Field('storage_location','text',length=1000),
		Field('storage_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
		Field('storage_temparature','double',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-400,400,error_message='from -400 to +400 in celsius')),label='Storage Temparature (in Celsius)'),
		Field('preparation_protocol','text',length=8000,label='Sample Preparation Protocol Description'),
                Field('preparation_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
		Field('storage_condition','text',length=1000),
		Field('sample_extraction_times','integer',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,6))),singular='Extr Preparation',plural='Extr Preparation')



#3.1.1 GC
db.define_table('gas_chromatography',
    Field('sample_name','reference sample', writable = False),
    Field('sample_id','integer',notnull=True,required=True,requires=IS_INT_IN_RANGE(0,100000000,error_message='Enter a positive number')),
    Field('sample_extraction_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),label='Date of sample Extraction'),
    Field('sample_extraction_desc','text',length=5000,label='Sample Processing and Extraction'),
    Field('extraction_solvent','text',length=1000),
    Field('extraction_protocol','text'),
    Field('extraction_volume','double',label='Extraction Volume (ml)',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,1000,error_message='too large !!'))),
    Field('resuspension_process','text',length=5000,label='Extract Concentration and Resuspension Process'),
    Field('extract_cleanup','text',length=5000,label='Extract Clean-Up'),
    Field('storage_description','text',length=5000),
    Field('storage_location','text',length=1000),
    Field('storage_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_temparature','double',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-400,400,error_message='from -400 to +400 in celsius')),label='Storage Temparature (in Celsius)'),
    Field('preparation_protocol','text',length=8000,label='Sample Preparation Protocol Description'),
    Field('preparation_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_condition','text',length=1000),
    Field('sample_extraction_times','integer',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,6))),
#GC
    Field('instrument_manufacturer','string',label='Manufacturer'),
    Field('instrument_model_name','string',label='Model name/number'),
    Field('instrument_software_package','string',label='Software package'),
    Field('instrument_version_number_or_date','string',label='Version number or Date'),
#3.1.2 GC
    Field('sample_phase','string',requires=IS_EMPTY_OR(IS_IN_SET(['polar','non-polar']))),
    Field('derivatization_method','string',label='Method'),
    Field('reagents_used_for_derivation','string',label='Reagents used for Derivatization'),
    Field('derivatization_temperature','string',label='Derivatization temperature (in degree centigrade)'),
    Field('derivatization_duration','string',label='Duration(in min)'),
#3.1.3
    Field('injector_model','string',label='Injector model/type'),
    Field('injector_software_version','string',label='Software version'),
    Field('method_name','text',label='Method name (used for sample injection)'),
    Field('injection_volume','string'),
    Field('wash_cycles','string',label='Wash cycles(volumes)'),
    Field('solvent','string'),
    Field('sample_size','string',label='Sample size/concentration'),
#3.1.41
    Field('column_manufacturer','string',label='Manufacturer'),
    Field('product_name_and_catalogue_number_of_column','string',label='Product Name and catalogue number (year of catalogue)'),
    Field('stationary_media_composition','string',requires=IS_NOT_EMPTY()),
    Field('internal_diameter_of_column','string'),
    Field('length_of_column','string'),
    Field('column_temperature_program','text'),
    Field('column_head_pressure','string',label='Column head pressure(in psi)'),
    Field('flow_rate','double',label='Flow rate(in mL/min)'),
#3.1.5
    Field('seperation_method_name','string',label='Method name'),
    Field('injector_temperature','string',label='Injector tempreature(in degree*c)'),
    Field('split_splitless_mode','string',requires=IS_EMPTY_OR(IS_IN_SET({'0':'Split mode','1':'Splitless mode'})),label='Split or splitless mode'),
    Field('split_ratio','string'),
    Field('mobile_phase_composition','text'),
    Field('mobile_phase_flow_rate','double',label='Mobile phase flow rate(in ml/min)'),
    Field('thermal_gradient_profiles','text',length='1000'),

#3.1.6
    Field('validation_sample','string'),
    Field('internal_standards','string'),
    Field('external_standards','string'),
    Field('chromatographic_resolution','string'),
    Field('cycle_per_column','integer'),
    Field('cycle_per_injector','integer'),
    Field('cycle_per_septum','string'),
    Field('cycle_per_blank','integer'),
    Field('detector','string'),
#3.1.7
    Field('SOP_protocol_name','string'),
    Field('date_of_analysis','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('operator','reference auth_user'),
    Field('deviation_from_SOP','text',length=1000),
    Field('tergetted_or_untargtted_approach',requires=IS_EMPTY_OR(IS_IN_SET({'0':'Targetted Approach','1':'Untargetted Approach'})),label='Approach'),
    Field('publication_refernce','text',length=1000,label='Publication reference(If any)'),plural='GC')

#LC
db.define_table('liquid_chromatography',
    Field('sample_name','reference sample', writable = False),
    Field('sample_id','integer',notnull=True,required=True,requires=IS_INT_IN_RANGE(0,100000000,error_message='Enter a positive number')),
    Field('sample_extraction_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())),label='Date of sample Extraction'),
    Field('sample_extraction_desc','text',length=5000,label='Sample Processing and Extraction'),
    Field('extraction_solvent','text',length=1000),
    Field('extraction_protocol','text'),
    Field('extraction_volume','double',label='Extraction Volume (ml)',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,1000,error_message='too large !!'))),
    Field('resuspension_process','text',length=5000,label='Extract Concentration and Resuspension Process'),
    Field('extract_cleanup','text',length=5000,label='Extract Clean-Up'),
    Field('storage_description','text',length=5000),
    Field('storage_location','text',length=1000),
    Field('storage_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_temparature','double',requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-400,400,error_message='from -400 to +400 in celsius')),label='Storage Temparature (in Celsius)'),
    Field('preparation_protocol','text',length=8000,label='Sample Preparation Protocol Description'),
    Field('preparation_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('storage_condition','text',length=1000),
    Field('sample_extraction_times','integer',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,6))),
#LC    
    Field('instrument_manufacturer','string',label='Manufacturer'),
    Field('instrument_model_name_ornumber','string',label='Model name/number'),
    Field('instrument_software_package','string',label='Software package'),
    Field('instrument_version_number_or_date','string',label='Version number or Date'),
#3.1.3
    Field('injector_model','string',label='Injector model/type'),
    Field('injector_software_version','string',label='Software version'),
    Field('method_name','text',label='Method name (used for sample injection)'),
    Field('injection_volume','string'),
    Field('wash_cycles','string',label='Wash cycles(volumes)'),
    Field('solvent','string'),
    Field('sample_size_or_concentration',label='Sample size/concentration'),
#3.1.41
    Field('column_manufacturer','string',label='Manufacturer'),
    Field('product_name_and_catalogue_number_of_column','string',label='Product Name and catalogue number (year of catalogue)'),
    Field('stationary_media_composition','string'),
    Field('internal_diameter_of_column','string'),
    Field('length_of_column','text'),
    Field('column_temperature_program','text'),
    Field('column_head_pressure','double',label='Column head pressure(in psi)'),
    Field('flow_rate','double',label='Flow rate(in mL/min)'),
#3.1.5
    Field('seperation_method_name','string',label='Method name'),
    Field('injector_temperature','string',label='Injector tempreature(in degree*c)'),
    Field('split_splitless_mode','string',requires=IS_EMPTY_OR(IS_IN_SET(['Split mode','Splitless mode'])),label='Split or splitless mode'),
    Field('split_ratio','string'),
    Field('mobile_phase_composition','text'),
    Field('mobile_phase_flow_rate','double',label='Mobile phase flow rate(in ml/min)'),
    Field('solvent_gradient_profiles','text',length='1000'),
#3.1.6
    Field('validation_sample','string'),
    Field('internal_standards','string'),
    Field('external_standards','string'),
    Field('chromatographic_resolution','string'),
    Field('chromatographic_resolution','string'),
    Field('cycle_per_column','integer'),
    Field('cycle_per_injector','integer'),
    Field('cycle_per_septum','string'),
    Field('cycle_per_blank','integer'),
    Field('detector','string'),
#3.1.7
    Field('SOP_protocol_name','string'),
    Field('date_of_analysis','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),
    Field('operator','reference auth_user'),
    Field('deviation_from_SOP','text',length=1000),
    Field('tergetted_or_untargtted_approach',requires=IS_EMPTY_OR(IS_IN_SET({'0':'Targetted Approach','1':'Untargetted Approach'})),label='Approach'),
    Field('publication_refernce','text',length=1000,label='Publication reference'),plural='LC')

# main table for  3.2 
db.define_table('mass_spectroscopy',

# table 3.2.1
     Field('sample_name','reference sample', writable = False),
     Field('manufacturer','string',),    
     Field('model','string',),    
     Field('oper_soft_name','string',label='operational software name ',),    
     Field('oper_soft_ver','string',label='operational software version',),   

# table 3.2.2
     Field('ionization_mode','string',required=False),    
     Field('polarity','string',required=False),    
     Field('vaccum_pressure','string'),    
     Field('len_voltages','string',label=' skimmer/focusing lens voltages '),    
     Field('gas_flows','string'),    
     Field('sour_temp','string',label='source temperature'),    

      
# table 3.2.3
     Field('type_of_analyzer','string'),    
     Field('m_range','string',label='m/z_range'),    
     Field('calibration_date','date',requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today()))),    
     Field('resolution1','string',label='resolution'),    
     Field('mass_accuracy1','string',label='mass accuracy'),    
     Field('log_program','string',label='logic program for data acquistion'),    
     Field('spectral_acquisition_rate','string'),    
     Field('vaccum_pressure','string'),    
     Field('concentration','string'),    
     Field('lock_mass','string'),    
     Field('flow_rate','string'),    
     Field('frequency','string'),    
     Field('add_info','text',label='additional information '),


# table 3.2.4
     Field('tune','string'),
     Field('sensitivity','string'),
     Field('mass_accuracy2','string',label='mass accuracy'),
     Field('resolution2','string',label='resolution'),

      
# table 3.2.5
     Field('SOP_protocol','text'),
     Field('date_of_data_acquistion','date'),
     Field('operator','string'),
     Field('data_acquisition_rate','string'),
     
     Field('deviation_from_SOP','string'),

     Field('replicate_sample_analysis','integer'),plural='MS')


db.define_table('spectrophotometry',

# table 3.2.1
     Field('sample_name','reference sample', writable = False),
     Field('wavelength','string'),
     Field('optical_density','string'),
     Field('Final_concentration_of_compound','string'),plural='SPM')

db.define_table('raw_data_storage_information',
    Field('sample_name','reference sample',writable=False),
    Field('email_id_of_person','string',label='Email id',required=True,requires=IS_EMAIL()),
    Field('identification_of_metabolites','text',label='Identification Of Metabolites'),
    Field('no_of_perks','integer',label='Number of Peaks'),
    Field('no_of_peaks_unidentified','integer',label='Number of Unidentified Peaks'),
    Field('number_of_metabolites','integer',label='Number Of Metabolites'),
    Field('referred_library','string',label='Referred Library and Version'), 
    Field('raw_data_file_name','string',label='Raw data file name'),
    Field('raw_data_file_upload','upload',label='Upload raw data file'),
    Field('raw_data_standard_format','string',label='Raw data standard format'),
    Field('raw_data_standard_format_upload','upload',label='Upload converted standard data file'),
    
    Field('additional_information_about_data','text',label='Additional information about data'),
    Field('additional_information_upload','upload',label='Additional data file upload'),
    Field('date_of_data_upload','date',label='Date of data uploaded',requires=IS_DATE_IN_RANGE(format='%d-%m-%Y',maximum=datetime.date.today())
    ),plural='RDS')


db.define_table('feedback',
               Field('feedback_on',required=True),
               Field('feedback_body','text',required=True,requires=IS_NOT_EMPTY()),
               Field('feedback_by','reference auth_user',notnull=False))                                                              




db.define_table('sample_files',
		Field('sample','reference sample',readable=False,writable=False),
		Field('file','upload',label='Additional Sample Data',required=True,notnull=True),
		Field('user','reference auth_user',readable=False,writable=False),
		Field('description','text'),format='%(sample)s')


def name(identifier):
   ans = db(db.auth_user.id == identifier).select().first()
   f = str(ans.first_name)+' '+str(ans.last_name)
   return f
