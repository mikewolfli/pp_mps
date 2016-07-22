#!/usr/bin/env python
#coding:utf-8
"""
  Author:   10256603<mikewolf.li@tkeap.com>
  Purpose: 
  Created: 2016/3/15
"""

from peewee import *
import datetime

#单位对照表
Unit_Types=(
    ('SET','套'),
    ('PC','件'),
    ('M','米'),
    ('MM', '毫米'),
    ('Kg','千克'),
    ('m/s','米/秒'),
    ('s','秒'),
    ('CM','分米'),
)

mps_db = PostgresqlDatabase('pgmps',user='postgres',password='1q2w3e4r',host='localhost',)

class BaseModel(Model):
    class Meta:
        database=mps_db
        
'''域账号登陆，无需login_user表      
class login_user(BaseModel):
    employee = CharField(db_column='employee_id',primary_key=True,max_length=8)
    password = CharField(null=True)
    is_valided = BooleanField(default=True)
    
    class Meta:
        db_table='login_user'
'''

class s_employee(BaseModel):
    employee = CharField(db_column='employee_id',primary_key=True,max_length=8)
    name = CharField(null=True, max_length=32)
    department = CharField(max_length=64, null=True)
    email = CharField(max_length=128, null=True)
    skype_id = CharField(max_length=128, null=True)
    
    class Meta:
        db_table='s_employee'
        
class operate_point(BaseModel):
    employee = ForeignKeyField(s_employee)
    operate_point=CharField(null=True, max_length=64)
    latest_on = DateTimeField(null=True,formats='%Y-%m-%d %H:%M:%S')
        
class op_permission(BaseModel):
    employee = ForeignKeyField(s_employee, to_field='employee')
    perm_code = CharField(max_length=64)
    
    class Meta:
        db_table='op_permission'  
        
class login_log(BaseModel):
    employee = CharField(db_column='employee_id', max_length=8)
    log_status = BooleanField(null=True)
    login_time = DateTimeField(null=True)
    logout_time = DateTimeField(null=True)
    
    class Meta:
        db_table='login_log'

class mat_basic_info(BaseModel):
    mat_no = CharField(primary_key=True, max_length=18)
    mat_name_en = CharField(null=True,max_length=255)
    mat_name_cn = CharField(max_length=128)
    gross_weight = CharField(null=True)
    base_unit = CharField(null=True, choices=Unit_Types)
    mat_type = CharField(null=True)
    normt = CharField(null=True)
    old_mat_no = CharField(null=True)
    doc_no = CharField(null=True)
    size_dimen = CharField(null=True)
    parameter = CharField(null=True)
    
    class Meta:
        db_table='mat_basic_info'

class mat_extra_info(BaseModel):
    mat_no = ForeignKeyField(mat_basic_info)
    lgfsb = CharField(max_length=4, null=True)
    lgpro = CharField(max_length=4, null=True)
    mrp_controller = CharField(max_length=3, null=True)
    sbdkz = CharField(max_length=1, null=True)
    prod_scheduler=CharField(max_length=3, null=True)
    sobsk = CharField(max_length=2, null=True)
    proc_type = CharField(max_length=1, null=True)
    spec_proc_type = CharField(max_length=2, null=True)
    matgr = CharField(max_length=20, null=True)
    mat_freight_group = CharField(null=True)
    plant = CharField(max_length=4, null=True)
    price_con_ind = CharField(max_length=1, null=True)
    val_type = CharField(max_length=10, null=True)
    val_area = CharField(max_length=4, null=True)
    val_class = CharField(max_length=4, null=True)
    remarks = TextField(null=True)
    
    class Meta:
        db_table='mat_extra_info'
        
class mat_alias_info(BaseModel):
    mat_no = CharField(primary_key=True,max_length=18)
    mat_name_alias = CharField(null=True, max_length=128)
    mat_type = CharField(null=True, max_length=64)
    mat_spec = CharField(null=True, max_length=64)
    mat_mat = CharField(null=True, max_length=64)
    remarks = TextField(null=True)
        
    class Meta:
        db_table='mat_alias_info'

class project_schedule(BaseModel):
    proj_sch_index = CharField(primary_key=True,max_length=32)
    product_date = DateField(formats='%Y-%m-%d')
    item = IntegerField(db_column='item_id')
    batch_id=CharField(null=True, max_length=48)
    mat_type = CharField(null=True, max_length=64)
    mat_spec = CharField(null=True, max_length=64)
    mat_mat = CharField(null=True, max_length=64)
    mat_desc = CharField(null=True, max_length=255)
    lift_type = CharField(null=True, max_length=32)
    project_name = CharField(null=True, max_length=255)
    rel_list = CharField(null=True,max_length=255) #wbs no or sto
    spn_date = DateField(formats='%Y-%m-%d', null=True)
    packing_info = CharField(null=True, max_length=255)
    qty = DecimalField(max_digits=10, decimal_places=3, auto_round=True)
    second_in_date = TextField(null=True)
    remarks = TextField(null=True)
    create_by = CharField(max_length=12)
    create_on = DateTimeField(default=datetime.datetime.now)
        
    class Meta:
        db_table='project_schedule'
        
class prod_orders_table(BaseModel):
    item = PrimaryKeyField(db_column='item_id')
    prod_order = CharField(max_length=24, index=True)
    batch_id = CharField(null=True)
    plant = CharField(max_length=4)
    mat_no = CharField(max_length=18)
    mat_name = CharField(max_length=128)
    wbs_no_box = CharField(null=True, max_length=32)
    mrp_controller= CharField(null=True, max_length=16)
    prod_scheduler = CharField(null=True, max_length=16)
    lift_type_d = CharField(null=True)
    spn_date = DateField(formats='%Y-%m-%d', null=True)
    req_qty = DecimalField(max_digits=10, decimal_places=3, auto_round=True)
    receive_qty = DecimalField(max_digits=10, decimal_places=3, auto_round=True, default=0.0)
    start_date = DateField(formats='%Y-%m-%d', null=True)
    fin_date = DateField(formats='%Y-%m-%d', null=True)
    order_status = CharField(null=True, max_length=32)
    order_type = CharField(null=True, max_length=32)
    remarks = TextField(null=True)
    create_by = CharField(max_length=12)
    create_on = DateTimeField(default=datetime.datetime.now)
    proj_sch_index = ForeignKeyField(project_schedule,to_field='proj_sch_index', null=True)
        
    class Meta:
        auto_increment=True
        db_table='prod_orders_table'

class powder_coated_schedule(BaseModel):
    proj_sch_index = CharField(primary_key=True, max_length=32)
    line_no = CharField(max_length=1, null=True)
    power_coated_area = DecimalField(max_digits=8, decimal_places=2, auto_round=True)
    hang_up_start = DateTimeField(formats='%Y-%m-%d %H:%M:%S',null=True)
    hang_up_fin = DateTimeField(formats='%Y-%m-%d %H:%M:%S',null=True)
    loop_time = TimeField(formats='%H:%M:%S',default='2:00:00')
    hang_down_start = DateTimeField(formats='%Y-%m-%d %H:%M:%S',null=True)
    hang_down_fin = DateTimeField(formats='%Y-%m-%d %H:%M:%S',null=True)
    remarks = TextField(null=True)
    
    class Meta:
        db_table='powder_coated_schedule'    

class number_counter(BaseModel):
    item = PrimaryKeyField(db_column='item_id')
    counter_step = IntegerField(null=True)
    current_counter = BigIntegerField(null=True)
    fol_char = CharField(null=True, max_length=16)
    pre_char = CharField(null=True, max_length=16)
    start_counter = IntegerField(null=True)
    
    class Meta:
        db_table = 'number_counter'

class powder_per_unit(BaseModel):
    item = PrimaryKeyField(db_column='item_id')
    mat_type = CharField(null=True, max_length=64)
    mat_spec = CharField(null=True, max_length=64)
    mat_mat = CharField(null=True, max_length=64)
    powder_use = DecimalField(max_digits=5, decimal_places=2, auto_round=True)
    
    class Meta:
        db_table = 'powder_per_unit'
        
pg_db = PostgresqlDatabase('pgworkflow',user='postgres',password='1q2w3e4r',host='10.127.144.62',)

class PgBaseModel(Model):
    class Meta:
        database=pg_db

class ProjectInfo(PgBaseModel):
    branch = CharField(db_column='branch_id', null=True)
    branch_name = CharField(null=True)
    contract = CharField(db_column='contract_id', null=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    plant = CharField(null=True)
    project = CharField(db_column='project_id', primary_key=True)
    project_name = TextField()
    res_emp = CharField(db_column='res_emp_id', null=True)
    
    class Meta:
        db_table = 's_project_info'
            
class ElevatorTypeDefine(PgBaseModel):
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    elevator_type = CharField()
    elevator_type_id = CharField(primary_key=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
        
    class Meta:
        db_table = 's_elevator_type_define'
                
class UnitInfo(PgBaseModel):
    can_psn = BooleanField(null=True)
    cancel_times = IntegerField(null=True)
    conf_batch = CharField(db_column='conf_batch_id', null=True)
    conf_valid_end = DateField(null=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    e_nstd = CharField(db_column='e_nstd_id', null=True)
    elevator = ForeignKeyField(db_column='elevator_id', null=True, rel_model=ElevatorTypeDefine, to_field='elevator_type_id')
    has_nonstd_inst_info = BooleanField(null=True)
    is_batch = BooleanField(null=True)
    is_urgent = BooleanField(null=True)
    lift_no = CharField(null=True)
    m_nstd = CharField(db_column='m_nstd_id', null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    nonstd_level = IntegerField(null=True)
    project_catalog = IntegerField(null=True)
    project = CharField(db_column='project_id', null=True)
    req_configure_finish = DateTimeField(null=True)
    req_delivery_date = DateTimeField(null=True)
    restart_times = IntegerField(null=True)
    review_is_urgent = BooleanField(null=True)
    review_valid_end = DateField(null=True)
    status = IntegerField(null=True)
    unit_doc = CharField(db_column='unit_doc_id', null=True)
    version = IntegerField(db_column='version_id', null=True)
    wbs_no = CharField(primary_key=True)
    wf_status = CharField(null=True)
            
    class Meta:
        db_table = 's_unit_info'