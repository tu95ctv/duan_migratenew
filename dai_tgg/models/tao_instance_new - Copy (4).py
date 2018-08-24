 # -*- coding: utf-8 -*-
import re
import xlrd
import time
import datetime
from odoo.exceptions import UserError
from odoo import  fields
import base64
from copy import deepcopy
import logging
from unidecode import unidecode
_logger = logging.getLogger(__name__)
from odoo.osv import expression
import sys
VERSION_INFO   = sys.version_info[0]
from collections import  OrderedDict

def get_or_create_object_has_x2m (self, class_name, search_dict,
                                write_dict ={},
                                is_must_update=False, 
                                noti_dict=None,
                                inactive_include_search = False, x2m_key=[],remove_all_or_just_add_one_x2m = True,
                                is_return_get_or_create = False,
#                                  not_update_field_if_instance_exist_list=[],
#                                  dict_get_or_create_para_all_field={},
                                 model_dict = {},
                                 key_tram =  None
                                 ):
    
    if x2m_key:
        first_values = search_dict[x2m_key[0]]
        result = []
        for key_first_value in first_values:
            search_dict[x2m_key[0]] = key_first_value
            object, get_or_create = get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search,is_return_get_or_create=True,
#                                     not_update_field_if_instance_exist_list=not_update_field_if_instance_exist_list,
#                                     dict_get_or_create_para_all_field = dict_get_or_create_para_all_field,
                                    model_dict = model_dict,
                                    key_tram = key_tram
                                    )
            result.append(object.id)
        if remove_all_or_just_add_one_x2m == True:
            six_or_zero = 6
            obj_id =  [(six_or_zero,False,result)]
        else:
            six_or_zero = 4
            obj_id =  [(4,result[0],False)]
    else:
        obj, get_or_create =  get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search, is_return_get_or_create=True,
#                                     not_update_field_if_instance_exist_list=not_update_field_if_instance_exist_list,
#                                     dict_get_or_create_para_all_field = dict_get_or_create_para_all_field,
                                    model_dict = model_dict,
                                    key_tram = key_tram

                                    
                                    )
        obj_id = obj.id
    if is_return_get_or_create:
        return obj_id, get_or_create
    else:
        return obj_id


        

def get_or_create_object_sosanh(self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False,
                                is_return_get_or_create = False,
#                                 dict_get_or_create_para_all_field={},
                                model_dict = {},
                                key_tram = None                               
                                ):
    
    
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
    else:
        this_model_noti_dict = None
    if inactive_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
    domain = []
    for i in search_dict:
        field_attr = model_dict['fields'][i]
#         get_or_create_para = field_attr.get('get_or_create_para',{})
        get_or_create_para = get_key_allow(field_attr, 'get_or_create_para', key_tram, {})
        operator_search = get_or_create_para.get('operator_search','=')
        tuple_in = (i,operator_search,search_dict[i])
        domain.append(tuple_in)
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
        search_dict.update(write_dict)
        #print '***search_dict***',search_dict
        created_object = self.env[class_name].create(search_dict)
        if this_model_noti_dict !=None:
            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
        return_obj =  created_object
    else:
        new_write_dict ={}
        for f_name in write_dict:
            not_update_field_if_instance_exist = model_dict['fields'][f_name].get('get_or_create_para',{}).get('not_update_field_if_instance_exist',False)
            if not not_update_field_if_instance_exist:
                new_write_dict[f_name] = write_dict[f_name]
        write_dict = new_write_dict
        if not is_must_update:
            is_write = False
            for f_name in write_dict:
                field_dict_val = write_dict[f_name]
                orm_field_val = getattr(searched_object, f_name)
                try:
                    converted_orm_val_to_dict_val = getattr(orm_field_val, 'id', orm_field_val)
                    if converted_orm_val_to_dict_val == None: #recorderset.id ==None when recorder sset = ()
                        converted_orm_val_to_dict_val = False
                except:#not singelton
                    pass
                if isinstance(orm_field_val, datetime.date):
                    converted_orm_val_to_dict_val = fields.Date.from_string(orm_field_val)
                if converted_orm_val_to_dict_val != field_dict_val:
                    is_write = True
                    break
        else:
            is_write = True
        if is_write:
            searched_object.write(write_dict)
            if this_model_noti_dict !=None:
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
        else:#'not update'
            if this_model_noti_dict !=None:
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        return_obj = searched_object
    if is_return_get_or_create:
        return return_obj, bool(searched_object)
    else:
        return return_obj

EMPTY_CHAR = [u'',u' ',u'\xa0']
def check_is_string_depend_python_version(val):
    if VERSION_INFO==2:
        check_str = isinstance(val,unicode) or isinstance(val,str)
    else:
        check_str =  isinstance(val,str)
    return check_str
    
def empty_string_to_False(readed_xl_value):
    if VERSION_INFO==2:
        check_str = isinstance(readed_xl_value,unicode) or isinstance(readed_xl_value,str)
    else:
        check_str =  isinstance(readed_xl_value,str)
    
    if check_str :
        if readed_xl_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_xl_value)
        if not rs:
            return False
    return readed_xl_value





# def active_function(val):
#     return False if val ==u'na' else True

def read_merge_cell(sheet,row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            break
    val = sheet.cell_value(row,col)
    return val

def read_excel_cho_field(sheet, row, col_index,merge_tuple_list):
    #print 'row','col',row, col_index,sheet
    val = read_merge_cell(sheet, row ,col_index,merge_tuple_list)
    if VERSION_INFO==2:
        check_str = isinstance(val,unicode) or isinstance(val,str)
    else:
        check_str =  isinstance(val,str)
    if check_str:
        #sai roi
        val = val.strip()
    #print 'val',val
#     val = empty_string_to_False(val)
    return val
            
### Xong khai bao

def f_ordered_a_model_dict(model_dict):
    fields = model_dict['fields']
    for fname,attr in fields:
        childrend_model_dict=  attr
        childrend_fields = childrend_model_dict.get('fields')
        if childrend_fields:
            new_ordered_dict = f_ordered_a_model_dict(childrend_model_dict)
    model_dict['fields']=OrderedDict(fields)
            


def rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,MODEL_DICT):
    print ('in rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR...')
    model_name = MODEL_DICT['model']
    fields= self.env[model_name]._fields
    for field_tuple in MODEL_DICT.get('fields',{}).items():
        f_name = field_tuple[0]
        field_attr = field_tuple[1]
        if not field_attr.get('for_excel_readonly') and f_name not in fields:
            raise UserError(u'field %s không có trong  danh sách fields của model %s'%(f_name,model_name))
#         if field_attr.get('xl_title'):
#                 field_attr[ 'xl_title_unidecode'] = unidecode(field_attr[u'xl_title'])
        if not field_attr.get('for_excel_readonly'):
            field = fields[f_name]
            field_attr['field_type'] = field.type
            if field.comodel_name:
                field_attr['model'] = field.comodel_name
                rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,field_attr)
def get_key_allow(field_attr, attr, key_tram,default_if_not_attr=None):
    value = field_attr.get(attr,default_if_not_attr)
    if isinstance(value, dict) and key_tram:
        value = value.get(key_tram,default_if_not_attr) or value.get('all_key_tram',default_if_not_attr)
    return value
    
def lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE_OLD(MODEL_DICT, value_may_be_title, col,key_tram):
    #print 'value_may_be_title',value_may_be_title
    print ('in lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE...')
#     if value_may_be_title ==u'Ngăn':
#         raise UserError(u'kakaka Ngăn')
    is_map_xl_title = False
#     is_map_xl_title_foreinkey = False
    for field,field_attr in MODEL_DICT.get('fields',{}).items():
        is_real_xl_match_with_xl_excel = False
        if field_attr.get('set_val',None) != None:
            continue
        elif get_key_allow(field_attr, 'skip_this_field', key_tram, False):
            continue
        if field_attr.get('xl_title') ==None and field_attr.get('col_index') !=None:
            continue# cos col_index
      
        elif field_attr.get('fields'):
            is_real_xl_match_with_xl_excel = lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE_OLD(field_attr, value_may_be_title, col)
        elif field_attr.get('xl_title'):
            if isinstance(field_attr['xl_title'], list):
                xl_title_s =  field_attr['xl_title']
            else:
                xl_title_s = [field_attr['xl_title']]
            for xl_title in xl_title_s:
                if xl_title == value_may_be_title:
#                     if xl_title ==u'Ngăn' and value_may_be_title==u'Ngăn':
#                         raise UserError(u'kakaka Ngăn')
                    field_attr['col_index'] = col
                    is_real_xl_match_with_xl_excel = True        
        is_map_xl_title = is_map_xl_title or is_real_xl_match_with_xl_excel
    return is_map_xl_title #or is_map_xl_title_foreinkey

def lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE(MODEL_DICT, value_may_be_title, col,key_tram):
    #print 'value_may_be_title',value_may_be_title
    print ('in lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE...')
    print ('key_tram',key_tram)
#     if value_may_be_title ==u'Ngăn':
#         raise UserError(u'kakaka Ngăn')
    is_map_xl_title = False
#     is_map_xl_title_foreinkey = False
    for field,field_attr in MODEL_DICT.get('fields',{}).items():
        is_real_xl_match_with_xl_excel = False
        xl_title = get_key_allow(field_attr,'xl_title',key_tram,None)
        if get_key_allow(field_attr,'set_val',key_tram,None) != None:
            continue
        if xl_title ==None and get_key_allow(field_attr,'col_index',key_tram,None) !=None:
            continue# cos col_index
        elif field_attr.get('fields'):
            is_real_xl_match_with_xl_excel = lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE(field_attr, value_may_be_title, col,key_tram)
        elif xl_title:
            if isinstance(xl_title, list):
                xl_title_s = xl_title
            else:
                xl_title_s = [xl_title]
            for xl_title in xl_title_s:
                if xl_title == value_may_be_title:
                    field_attr['col_index'] = col
                    is_real_xl_match_with_xl_excel = True        
        is_map_xl_title = is_map_xl_title or is_real_xl_match_with_xl_excel
    return is_map_xl_title #or is_map_xl_title_foreinkey

def create_instance (self, MODEL_DICT, sheet, row, merge_tuple_list,needdata, noti_dict, main_call_create_instance = None,
                     key_tram=None):
    key_search_dict = {}
    update_dict = {}
    vof_dict = {} # value of fields of one instance
    model_name = MODEL_DICT['model']
    if main_call_create_instance == model_name:
        needdata['vof_dict'] = vof_dict
    x2m_key = []
    remove_all_or_just_add_one_x2m = True
    for field_name,field_attr  in MODEL_DICT['fields'].items():
        if get_key_allow(field_attr, 'skip_this_field', key_tram, False):
            continue
        col_index = field_attr.get('col_index')
        xl_val = False
        field_type_of_this_model = MODEL_DICT.get('field_type')
        xl_title = get_key_allow(field_attr, 'xl_title', key_tram)#moi them , moi bo field_attr.get('xl_title')
        if col_index == None and xl_title:
            is_match =  False
        else:
            is_match = True
        if not is_match:
            sheet_allow_this_field_not_has_exel_col =get_key_allow( field_attr,'sheet_allow_this_field_not_has_exel_col',key_tram)
            skip_field_if_not_found_column_in_some_sheet = get_key_allow(field_attr,'skip_field_if_not_found_column_in_some_sheet',key_tram)
            allow_not_match =  skip_field_if_not_found_column_in_some_sheet or (sheet_allow_this_field_not_has_exel_col and needdata['sheet_name'] in sheet_allow_this_field_not_has_exel_col)
            if not allow_not_match:
                raise UserError(u'có khai báo xl_title nhưng không match với file excel, field: %s, xl_title: %s, dòng: %s ' %(field_name,field_attr.get('xl_title'),row))
        avof_dict = vof_dict.setdefault(field_name,{})
        
        set_val = get_key_allow( field_attr,'set_val',key_tram)
        if set_val != None:
            xl_val = set_val
        elif field_attr.get('skip_field_cause_first_import'):
            continue
       
        elif col_index !=None: # đọc file exc
            xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
            avof_dict['excel_val'] = xl_val
            xl_val = empty_string_to_False(xl_val)
            if xl_val   != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('x2m_list'):
                xl_val = xl_val.split(',')
                xl_val = map(lambda i: i.strip(),xl_val)
        
        elif field_attr.get('fields') :#and field_attr.get('field_type')=='many2one':
            xl_val, vof_dict_childrend, get_or_create  = create_instance (self, field_attr, sheet, row, merge_tuple_list, needdata, noti_dict,key_tram=key_tram)
            avof_dict['fields'] = vof_dict_childrend
            avof_dict['get_or_create'] = get_or_create

        avof_dict['before_func_val'] = xl_val
        set_val = get_key_allow( field_attr,'set_val',key_tram)
        
        func = get_key_allow( field_attr,'func',key_tram)
        print ("key_tram",key_tram)
        karg = get_key_allow( field_attr,'karg',key_tram,{})
        print ('func',func)
        xl_val = func(xl_val, needdata,**karg) if func else xl_val
        replace_string = get_key_allow( field_attr,'replace_string',key_tram)
        if  replace_string and check_is_string_depend_python_version(xl_val):
            for pattern,repl in replace_string:
                xl_val = re.sub(pattern, repl, xl_val)
        empty_val = get_key_allow( field_attr,'empty_val',key_tram)
        if empty_val and xl_val in empty_val:
            xl_val = False   
       
        replace_val = get_key_allow( field_attr,'replace_val',key_tram)
        if replace_val:
            replace_val_tuple = replace_val.get(needdata['sheet_name']) or replace_val.get('all')
            if replace_val_tuple:
                for k,v in replace_val_tuple:
                    if xl_val ==k:
                        xl_val = v
                        break
        if xl_val == False and  field_attr.get('default'):
            xl_val = field_attr.get('default')
        avof_dict['val'] = xl_val
       
        required = field_attr.get('required',False)
        if required and xl_val==False:
            if field_attr.get('raise_if_False'):
                raise UserError('raise_if_False field: %s'%field_name)
            return False , vof_dict,False
        
        
        elif field_attr.get('bypass_this_field_if_value_equal_False') and xl_val==False:
            continue
        elif not field_attr.get('for_excel_readonly'):
            key_or_not = field_attr.get('key')
            if key_or_not==True:
                key_search_dict [field_name] = xl_val
            elif key_or_not == 'Both':
                key_search_dict [field_name] = xl_val
                update_dict [field_name] = xl_val
            else:
                update_dict [field_name] = xl_val
#         print ('4',count)
        if field_attr.get('x2m_list'):
                x2m_key.append(field_name)
                remove_all_or_just_add_one_x2m &= field_attr.get('remove_all_or_just_add_one_x2m',True)
                
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    
    if MODEL_DICT.get('last_function'):
        MODEL_DICT.get('last_function')(needdata)
    get_or_create = False
#     print ('key_search_dict',key_search_dict)
#     print ('update_dict',update_dict)
    if key_search_dict:
        obj_val, get_or_create = get_or_create_object_has_x2m(self, model_name, key_search_dict, update_dict,
                                is_must_update = True, 
                                noti_dict = noti_dict,
                                inactive_include_search  = inactive_include_search, 
                                x2m_key = x2m_key,
                                remove_all_or_just_add_one_x2m=remove_all_or_just_add_one_x2m,
                                is_return_get_or_create = True,
                                model_dict=MODEL_DICT,
                                key_tram = key_tram
                                )
    else:
        obj_val = False
    return obj_val, vof_dict, get_or_create



def convert_integer(val,needdata):
    try:
        return int(val)
    except:
        return 0
    


def qty_(val,n):
    if val:
        print ('val',val)
        val = int(val)
        val=  1 if  (n['vof_dict']['prod_lot_id_excel_readonly']['val'] and val > 1) else val
    return val
def importthuvien(odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    def lot_name_(val,needdata):
        p_id = needdata['vof_dict']['product_id']['val']
        product_id = self.env['product.product'].browse(p_id)
        UBC  = 'use barcode '
        lot_name = needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or (needdata['vof_dict']['barcode_for_first_read']['val'] and  (UBC +' ' + needdata['vof_dict']['barcode_for_first_read']['val']))
        if lot_name== UBC:
            lot_name= lot_name + str(int(needdata['vof_dict']['stt']['val']))
        elif  (lot_name ==False and  product_id.tracking=='serial'):
            lot_name = 'unknown ' + product_id.name + '  ' + str(int(needdata['vof_dict']['stt']['val']) )
#         print ("lot_name",lot_name,product_id.name,product_id.tracking,lot_name ==False )
        return lot_name
    def choose_inventory_id_name(v,n):
#         if not self.sheet_name:
#             return self.department_id.name
#         else:
#             return n['sheet_name']
        return self.import_location_id.name + '-' +  ','.join(n['sheet_names'])
    def last_record_function_ltk_vtdc_(n):
        if n['vof_dict']['product_id']['get_or_create']== False:# nếu product_id được tạo mới là sai
            raise UserError(u'Product %s  phải được tạo từ trước'%n['vof_dict']['product_id']['fields']['name']['val'])
        last_record_function_get_inventory_id_(n)
    
    def last_record_function_get_inventory_id_(n):
        print ("n['vof_dict']['inventory_id']['val']",n['vof_dict']['inventory_id']['val'])
        if n['vof_dict']['inventory_id']['val'] and  not needdata.get('inventory_id'):
            n['inventory_id'] = n['vof_dict']['inventory_id']['val']
        
    def convert_float_location_(v,n):
        if isinstance(v, float):
            v= str(int(v))
        return v

    def convert_float_to_ghi_chu_ngay_xuat(val):
        if isinstance(val, float):
            seconds = (val - 25569) * 86400.0
            try:
                val= datetime.datetime.utcfromtimestamp(seconds).strftime('%d/%m/%Y')
            except ValueError:# year is out of range
                pass
        return val 
        
            
    def last_import_function_get_self_inventory_id_():
        self.inventory_id = needdata['inventory_id']
    def name_of_uom_id_(v,n):
        v = u'Cái' if n['sheet_name']== u'XFP, SFP các loại' else v
        if isinstance(v,unicode) or isinstance(v,str):
            v = v.capitalize()
        return v
            
    SHEET_CONVERT = {'TTI':{u'CHUYỂN MẠCH':u'Chuyển Mạch (IMS, Di Động)',u'IP':u'IP (VN2, VNP)',u'TRUYỀN DẪN':u'Truyền dẫn',u'GTGT': u'GTGT',u'VÔ TUYẾN' :u'Vô tuyến'}}
    def categ_id_tti_convert_to_ltk_(v,n,tram=None):
#         raise UserError('kdkfasdlkfjld')
        v =  n['sheet_name']
        tram_dict = SHEET_CONVERT.get(tram)
        if tram_dict:
            return tram_dict.get(v,v)
        else:
            return v
    for r in self:
            recordlist = base64.decodestring(r.file)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            ALL_MODELS_DICT = {
               u'stock.inventory.line': {
                'title_rows':[4,5],
                'title_rows_some_sheets':{u'XFP, SFP các loại':[2,3]},
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name]  ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                'model':'stock.inventory.line',
                'last_function_for_import':last_import_function_get_self_inventory_id_,
                'last_function':last_record_function_get_inventory_id_,
                'fields' : [
                ('stt',{'func':None,'xl_title':u'STT new','key':True, 'required':True,'skip_field_if_not_found_column_in_some_sheet':True}),
                ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True, 'set_val':self.department_id.default_location_id.id,'raise_if_False':True}),  
                ('prod_lot_id_excel_readonly',{'empty_val':[u'N/C',],'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':[u'Seri Number'],'for_excel_readonly' :True}),
                ('product_qty', {'func':qty_,'replace_val':{u'XFP, SFP các loại':[(False,1)]},'xl_title':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],'key':False,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
                ('inventory_id', {'fields':[
                                        ('name',{'func':choose_inventory_id_name, 'key':True,'required': True}),
                                        ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                        ,]
                    }),
                ('product_id',{'key':True,'required':True,
                               'fields':[
                                        ('name',{'func':None,'xl_title':[u'TÊN VẬT TƯ',u'Module quang'],'key':True,'required':True,'empty_val':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000']}),
                                        ('type',{'set_val':'product'}),
                                        ('tracking',{'func':lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else False, 'bypass_this_field_if_value_equal_False':True}),
                                        ('thiet_bi_id',{'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
                                        ('brand_id',{'empty_val':[u'NA'],'fields':[('name',{'func':None,'xl_title':[u'Hãng sản xuất',u'Hãng / Model'], 'key':True,'required': True}),]}),
                                        ('categ_id',{'fields':[('name',{'func':lambda val,needdata: needdata['sheet_name'], 'key':True,'required': True}),]}),
                                        ('uom_id',  {'bypass_this_field_if_value_equal_False':True, 'fields': [ #'func':uom_id_,'default':1,
                                                    ('name',{
                                                             'func': name_of_uom_id_,
                                                             'get_or_create_para':{'operator_search':'=ilike'},
                                                             'xl_title':u'Đơn vị tính' ,'key':True,'required':True,
                                                              'replace_string':[('Modunle','module'),('CARD','Card'),('module','Module')],
                                                              'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']
                                                              }),#'set_val':u'Cái',
                                                             ('category_id', {'func': lambda n,v:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn Vị')])[0].id
                                                                                        }
                                                                 ),
                                      
                                                                       ]
                                                            }
                                         ),
                                         # Vật tư dự phòng LTK
                                        ('ghi_chu_ngay_nhap',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':[u'Ngày nhập',u'Ngày nhận'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('ghi_chu_ngay_xuat',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ngày xuất','skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('ghi_chu_ban_dau',{'func':lambda val,needdata: val if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ghi chú','skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('du_phong_tao',{'set_val':True}),
                                        ('tram_ltk_tao',{'set_val':True}),
                                        
                                        ]
                               }),  
                ('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':None,'xl_title':u'Phòng', 'key':True,'required': True,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                 ('stock_type',{'set_val':'phong_may'}),
                                                                ]
                                                       }), 
                ('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':None,'xl_title':[u'Tủ/Kệ',u'Tủ'], 'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
                                                               ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                                 
                                                                  ('stock_type',{'set_val':'tu'}),
                                                                
                                                                ]
                                                       }),                                           
                ('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':None,'xl_title':[u'Ngăn',u'Ngăn/Kệ'], 'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True }),
                                                                ('stock_type',{'set_val':'shelf'}),
                                                                
                                                                ]
                                                       }),         
                ('location_id4',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':None,'xl_title':[u'Số thùng'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                ('stock_type',{'set_val':'stt_trong_self'}),
                                                                ]
                                                       }),  
              ('location_id5',{'model':'stock.location', 'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{'func':convert_float_location_, 'xl_title':[u'Hộp'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                    ('stock_type',{'set_val':'slot'}),
                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                    ]
                                           }),                              
                ('location_id', {'func':lambda v,needdata: needdata['vof_dict']['location_id4']['val'] or \
                    needdata['vof_dict']['location_id3']['val'] or \
                    needdata['vof_dict']['location_id2']['val'] or \
                    needdata['vof_dict']['location_id1']['val'] or \
                    needdata['vof_dict']['location_id_goc']['val']
                    , 'key':True}),
                ('prod_lot_id', {'key':True,
                                  'fields':[
                                    ('name',{'func':lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],'key':True,'required':True}),
                                    ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],'key': True }),
                                    ('pn',{'xl_title':[u'Part Number',u'Partnumber']}),
                                    ('pn_id',{'model':'tonkho.pn',
                                                                  'fields':[
                                                                            ('name',{'empty_val':[u'NA','-','--'],'xl_title':[u'Part Number',u'Partnumber'],'key':True, 'required':True}),
                                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True  }),
                                                                            ('import_location_id',{'set_val': self.import_location_id.id}),
                                                                            ('du_phong_tao',{'set_val':True}),
                                                                            ('tram_ltk_tao',{'set_val':True}),
                                                                            ]
                                                                  }),
                                    ('ghi_chu_ngay_xuat',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_xuat']['before_func_val'])}),
                                   #copy
                                    ('ghi_chu_ngay_nhap',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_nhap']['before_func_val'])}),
                                    ('ghi_chu_ban_dau',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ban_dau']['before_func_val'])}),
                                      ]
                                  }),
                                         ]
                },#End stock.inventory.line'
                               
                 
                 u'stock.inventory.line.tong.hop.ltk.dp.tti.dp': { #tong hop
                'key_allow':True,
                'title_rows':{'key_ltk':[4,5],'key_tti':[3,4]},
                'title_rows_some_sheets':{'key_ltk':{u'XFP, SFP các loại':[2,3]}},
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names':{
                    'key_ltk':lambda self: [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name],
                    'key_tti':lambda self: [u'CHUYỂN MẠCH',u'IP',u'TRUYỀN DẪN',u'GTGT',u'VÔ TUYẾN']if not self.sheet_name else [self.sheet_name],
                               }  ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                'model':'stock.inventory.line',
                'last_function_for_import':last_import_function_get_self_inventory_id_,
                'last_function':last_record_function_get_inventory_id_,
                'fields' : [
                        ('stt',{'func':None, 'xl_title': {'key_ltk':u'STT new',
                                                                    'key_tti':u'STT'
                                                          },'key':True, 'required':True,'skip_field_if_not_found_column_in_some_sheet':True}),
                     
                        
                        ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True, 'set_val':self.department_id.default_location_id.id,'raise_if_False':True}),  
                ('prod_lot_id_excel_readonly',{'empty_val':{'key_ltk':[u'N/C'],
                                                                                    'key_tti':[u'N/C',u'N/a',u'n/a',u'N/A']
                                                            }, 'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':[u'Seri Number'],'for_excel_readonly' :True}),
                ('product_qty', {'func':qty_,'replace_val':{'key_ltk':{u'XFP, SFP các loại':[(False,1)]}},
                                 'xl_title':{'key_ltk':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                               'key_tti':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ']
                                             },
                                 'key':False,'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                
                ('inventory_id', {'fields':[
                                        ('name',{'func':choose_inventory_id_name, 'key':True,'required': True}),
                                        ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                        ,]
                    }),
                
                
                
                ('product_id',{'key':True,'required':True,
                               'fields':[
                                        ('name',{'func':None,
                                                 'xl_title':{'key_ltk':[u'TÊN VẬT TƯ',u'Module quang'],
                                                                'key_tti':[u'TÊN VẬT TƯ'],
                                                             },
                                                 'key':True,'required':True,
                                                 'empty_val':{'key_ltk':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000']}
                                                 
                                                 
                                                              }),
                                        ('type',{'set_val':'product'}),
                                        ('tracking',{'func':lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else False, 'bypass_this_field_if_value_equal_False':True}),
                                        ('thiet_bi_id',{
                                            'get_or_create_para':{'key_tti':{'not_update_field_if_instance_exist':True}},
                                            'fields':[('name',{'func':None,
                                                                           'xl_title':{'key_ltk':u'Thiết bị',
                                                                                       'key_tti':u'Thiết bị'}, 
                                                                           'key':True,'required': True}),]}),
                                      
                                        ('thiet_bi_id_tti',{'skip_this_field':{'key_ltk':True,
                                                                                             'key_tti':False},
                                        'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
                                         
                                           ('thiet_bi_id_ltk',{'skip_this_field':{'key_ltk':False,
                                                                                             'key_tti':True},
                                        'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
                                         
                                         
                                         
                                        ('brand_id',{'empty_val':[u'NA'],'fields':[('name',{'func':None,
                                                                                            'xl_title':{'key_ltk':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                            'key_tti':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                        },
                                                                                             'key':True,'required': True}),]}),
                                        ('categ_id',{'fields':[('name',{
                                            'func':{'all_key_tram':lambda val,needdata: needdata['sheet_name'],
                                                        'key_tti':categ_id_tti_convert_to_ltk_,
                                                    },
                                              'karg':{'key_tti':{'tram':'TTI'}},
                                             'key':True,'required': True}),]}),
                                        ('uom_id',  {'bypass_this_field_if_value_equal_False':True, 'fields': [ #'func':uom_id_,'default':1,
                                                    ('name',{'func':{'key_ltk': name_of_uom_id_ },
                                                             'get_or_create_para':{
                                                                                'all_key_tram':{'operator_search':'=ilike'},
                                                                                   },
                                                             'xl_title':u'Đơn vị tính' ,'key':True,'required':True,
                                                              'replace_string':{'key_ltk':[('Modunle','module'),('CARD','Card'),('module','Module')],
                                                                                        'key_tti':[('CARD','Card'),('module','Module'),(u'bộ',u'Bộ')]
                                                                                },
                                                             
                                                              'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']
                                                                                                         }
                                                              }),#'set_val':u'Cái',
                                                             ('category_id', {'func': lambda n,v:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn Vị')])[0].id
                                                                                        }
                                                                 ),
                                      
                                                                       ]
                                                            }
                                         ),
                                         # Vật tư dự phòng LTK
                                        ('ghi_chu_ngay_nhap',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':[u'Ngày nhập',u'Ngày nhận'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('ghi_chu_ngay_xuat',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ngày xuất','skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('ghi_chu_ban_dau',{'func':lambda val,needdata: val if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ghi chú','skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('du_phong_tao',{'set_val':True}),
                                        ('tram_ltk_tao',{'set_val':(r.key_tram and 'ltk' in r.key_tram), 'bypass_this_field_if_value_equal_False':True }),
                                        ('tram_tti_tao',{'set_val': (r.key_tram and 'tti' in r.key_tram), 'bypass_this_field_if_value_equal_False':True  }),
                                        ]
                               }),  
                ('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':u'Phòng',
                                                                                     'key_tti':u'Phòng'},
                                                                          'key':True,'required': True,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                 ('stock_type',{'set_val':'phong_may'}),
                                                                ]
                                                       }), 
                ('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Tủ/Kệ',u'Tủ'],
                                                                                        'key_tti':[u'Tủ/Kệ',u'Tủ']
                                                                                     },
                                                                          'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
                                                               ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                                 
                                                                  ('stock_type',{'set_val':'tu'}),
                                                                
                                                                ]
                                                       }),                                           
                ('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                        'key_tti':[u'Ngăn',u'Ngăn/Kệ']},
                                                                          'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True }),
                                                                ('stock_type',{'set_val':'shelf'}),
                                                                
                                                                ]
                                                       }),         
                ('location_id4',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Số thùng'],
                                                                                        'key_tti':[u'Số thùng']},                                                                          'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                ('stock_type',{'set_val':'stt_trong_self'}),
                                                                ]
                                                       }),  
              ('location_id5',{'model':'stock.location', 'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{'func':convert_float_location_,
                                                            'xl_title':{'key_ltk':[u'Hộp'],
                                                                        'key_tti':[u'Hộp']},        
                                                            'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                    ('stock_type',{'set_val':'slot'}),
                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                    ]
                                           }),                              
                ('location_id', {'func':lambda v,needdata: needdata['vof_dict']['location_id4']['val'] or \
                    needdata['vof_dict']['location_id3']['val'] or \
                    needdata['vof_dict']['location_id2']['val'] or \
                    needdata['vof_dict']['location_id1']['val'] or \
                    needdata['vof_dict']['location_id_goc']['val']
                    , 'key':True}),
                ('prod_lot_id', {'key':True,
                                  'fields':[
                                    ('name',{'func':lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],'key':True,'required':True}),
                                    ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],'key': True }),
                                    ('pn',{'xl_title':[u'Part Number',u'Partnumber']}),
                                    ('pn_id',{'model':'tonkho.pn',
                                                                  'fields':[
                                                                            ('name',{'empty_val':[u'NA','-','--'],'xl_title':[u'Part Number',u'Partnumber'],'key':True, 'required':True}),
                                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True  }),
                                                                            ('import_location_id',{'set_val': self.import_location_id.id}),
                                                                            ('du_phong_tao',{'set_val':True}),
                                                                            ('tram_ltk_tao',{'set_val':(r.key_tram and 'ltk' in r.key_tram)}),
#                                                                             ('tram_tti_tao',{'set_val': (r.key_tram and 'tti' in r.key_tram)}),
                                                                            ]
                                                                  }),
                                    ('ghi_chu_ngay_xuat',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_xuat']['before_func_val'])}),
                                   #copy
                                    ('ghi_chu_ngay_nhap',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_nhap']['before_func_val'])}),
                                    ('ghi_chu_ban_dau',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ban_dau']['before_func_val'])}),
                                      ]
                                  }),
                                         ]
                },#End stock.inventory.line'
                               
                #'TTI'
                 u'stock.inventory.line.dp_tti': {
                'title_rows':[3,4],
#                 'title_rows_some_sheets':{u'XFP, SFP các loại':[2,3]},
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'CHUYỂN MẠCH',u'IP',u'TRUYỀN DẪN',u'GTGT',u'VÔ TUYẾN']if not self.sheet_name else [self.sheet_name]  ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                'model':'stock.inventory.line',
                'last_function_for_import':last_import_function_get_self_inventory_id_,# last function in all
                'last_function':last_record_function_get_inventory_id_,# last function in  row
                'fields' : [
                        ('stt',{'func':None,'xl_title':u'STT','key':True, 'required':True}),
                        ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True, 'set_val':self.department_id.default_location_id.id,'raise_if_False':True}),  
                ('prod_lot_id_excel_readonly',{'empty_val':[u'N/C',u'N/a',u'n/a',u'N/A'],'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':[u'Seri Number'],'for_excel_readonly' :True}),
                ('product_qty', {'func':qty_,'replace_val':{u'XFP, SFP các loại':[(False,1)]},'xl_title':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],'key':False,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
                ('inventory_id', {'fields':[
                                        ('name',{'func':choose_inventory_id_name, 'key':True,'required': True}),
                                        ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                        ,]
                    }),
                ('product_id',{'key':True,'required':True,
                               'fields':[
                                        ('name',{'func':None,'xl_title':[u'TÊN VẬT TƯ',u'Module quang'],'key':True,'required':True,'empty_val':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000']}),
                                        ('type',{'set_val':'product'}),
                                        ('tracking',{'func':lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else False, 'bypass_this_field_if_value_equal_False':True}),
                                        ('thiet_bi_id',{
                                            'get_or_create_para':{'not_update_field_if_instance_exist':True}
                                            ,'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]
                                            }),
                                        ('thiet_bi_id_tti',{'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
                                        
                                        
                                        
                                        ('brand_id_tti',{'empty_val':[u'NA'],'fields':[('name',{'func':None,'xl_title':[u'Hãng sản xuất',u'Hãng / Model'], 'key':True,'required': True}),]}),
                                        ('categ_id',{'fields':[('name',{'func':categ_id_tti_convert_to_ltk_,'karg':{'tram':'TTI'},#lambda val,needdata: needdata['sheet_name'],
                                                                         'key':True,'required': True}),]}),
                                        ('uom_id',  {'bypass_this_field_if_value_equal_False':True, 'fields': [ #'func':uom_id_,'default':1,
                                                    ('name',{
                                                             'get_or_create_para':{'operator_search':'=ilike'},
                                                             'func':lambda v,n: u'Cái' if n['sheet_name']== u'XFP, SFP các loại' else v ,
                                                             'xl_title':u'Đơn vị tính' ,'key':True,'required':True,
                                                              'replace_string':[('Modunle','module'),('CARD','Card'),('module','Module'),
                                                                                (u'bộ',u'Bộ'),
# (u'cái',u'Cái'),(u'sợi',u'Sợi'),(u'jack nối',u'Jack nối')
                                                                                ],
                                                              'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']
                                                              }),#'set_val':u'Cái',
                                                             ('category_id', {'func': lambda n,v:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn Vị')])[0].id
                                                                                        }
                                                                 ),
                                      
                                                                       ]
                                                            }
                                         ),
                                         # Vật tư dự phòng LTK
                                        ('ghi_chu_ngay_nhap',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':[u'Ngày nhập',u'Ngày nhận'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('ghi_chu_ngay_xuat',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ngày xuất','skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('ghi_chu_ban_dau',{'func':lambda val,needdata: val if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ghi chú','skip_field_if_not_found_column_in_some_sheet':True}),
                                        ('du_phong_tao',{'set_val':True}),
                                        ('tram_tti_tao',{'set_val':True}),
                                        
                                        ]
                               }),  
                ('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,'xl_title':u'Phòng', 'key':True,'required': True,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                 ('stock_type',{'set_val':'phong_may'}),
                                                                ]
                                                       }), 
                ('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,'xl_title':[u'Tủ/Kệ',u'Tủ'], 'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
                                                               ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                                 
                                                                  ('stock_type',{'set_val':'tu'}),
                                                                
                                                                ]
                                                       }),                                           
                ('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,'xl_title':[u'Ngăn',u'Ngăn/Kệ'], 'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True }),
                                                                ('stock_type',{'set_val':'shelf'}),
                                                                
                                                                ]
                                                       }),         
                ('location_id4',{'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,'xl_title':[u'Số thùng'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                ('stock_type',{'set_val':'stt_trong_self'}),
                                                                ]
                                                       }),  
              ('location_id5',{'model':'stock.location', 'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{'func':convert_float_location_, 'xl_title':[u'Hộp'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                    ('stock_type',{'set_val':'slot'}),
                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                    ]
                                           }),                              
                ('location_id', {'func':lambda v,needdata: needdata['vof_dict']['location_id4']['val'] or \
                    needdata['vof_dict']['location_id3']['val'] or \
                    needdata['vof_dict']['location_id2']['val'] or \
                    needdata['vof_dict']['location_id1']['val'] or \
                    needdata['vof_dict']['location_id_goc']['val']
                    , 'key':True}),
                ('prod_lot_id', {'key':True,
                                  'fields':[
                                    ('name',{'func':lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],'key':True,'required':True}),
                                    ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],'key': True }),
                                    ('pn',{'xl_title':[u'Part Number',u'Partnumber']}),
                                    ('pn_id',{'model':'tonkho.pn',
                                                                  'fields':[
                                                                            ('name',{'empty_val':[u'NA','-','--'],'xl_title':[u'Part Number',u'Partnumber'],'key':True, 'required':True}),
                                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True  }),
                                                                            ('import_location_id',{'set_val': self.import_location_id.id}),
                                                                            ('du_phong_tao',{'set_val':True}),
                                                                            ('tram_ltk_tao',{'set_val':True}),
                                                                            ]
                                                                  }),
                                    ('ghi_chu_ngay_xuat',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_xuat']['before_func_val'])}),
                                   #copy
                                    ('ghi_chu_ngay_nhap',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_nhap']['before_func_val'])}),
                                    ('ghi_chu_ban_dau',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ban_dau']['before_func_val'])}),
                                      ]
                                  }),
                                         ]
                },#End stock.inventory.line LTK'
                               
                               
                               
                               
                u'Product': {
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Tổng hợp']if not self.sheet_name else [self.sheet_name],
                'model':'product.product',
                'for_excel_readonly' :True,
                'fields' : [
                        ('stt',{'func':None,'xl_title':u'STT','key':True,'required':True,'skip_field_if_not_found_column_in_some_sheet':True,'for_excel_readonly' :True}),
                        ('prod_lot_id_excel_readonly',{'empty_val':[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN'],'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':[u'Số serial (S/N)'],'for_excel_readonly' :True}),
                        ('barcode_for_first_read',{'empty_val':[u'NA',u"'",u"`"],'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,'xl_title':[u'Barcode'],'for_excel_readonly' :True}),
                        ('product_id',{ 'for_excel_readonly' :True,'model':'product.product',
                         'fields':[   
                        ('name',{'func':None,'xl_title':[u'Loại card'],'key':True,'required':True,'empty_val':[]}),
                        ('type',{'set_val':'product'}),
                        
                        ('dang_chay_tao',{'set_val':True}),
                        ('tram_ltk_tao',{'set_val':True}),
                        
                        ('tracking',{'func':lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else False,'bypass_this_field_if_value_equal_False':True}),
                        ('is_co_sn_khong_tinh_barcode',{'func':lambda val,needdata: True if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val']) !=False else False,'bypass_this_field_if_value_equal_False':True}),
                        ('thiet_bi_id',{'model':'tonkho.thietbi', 'fields':[('name',{'func':None,'xl_title':u'Tên hệ thống thiết bị', 'key':True,'required': True}),]}),
                        ('categ_id',{'model':'product.category','fields':[('name',{'func':lambda val,needdata: needdata['sheet_name'], 'key':True,'required': True}),]}),
                        ('uom_id',  {'model':'product.uom', 'fields': [ #'func':uom_id_,'default':1,
                                    ('name',{'set_val':u'Cái','key':True}),#'set_val':u'Cái',
                                             ('category_id', {'func': lambda n,v:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn Vị')])[0].id
                                                                        }
                                                 ),
                      
                                                       ]
                                            }
                         ),
                            ]
                         }),
                            
                            
                        ('prod_lot_id_readexcel', {'for_excel_readonly' :True,'model':'stock.production.lot',
                  'fields':[
                    ('name',{'func':lot_name_ ,'key':True,'required':True}),
                    ('barcode_sn',{'func':lambda v,n:n['vof_dict']['barcode_for_first_read']['val'] ,'key':True}),
                    ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] ,'key':True,'required':True}),
                    ('pn_id',{'model':'tonkho.pn',
                                                  'fields':[
                                                            ('name',{'empty_val':[u'NA','-','--'],'xl_title':[u'Mã card (P/N)'],'key':True, 'required':True}),
                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True  }),
                                                            ('import_location_id',{'set_val':self.import_location_id.id}),
                                                            ('dang_chay_tao',{'set_val':True}),
                                                            ('tram_ltk_tao',{'set_val':True}),
                                                            
                                                            ]
                                                  }),
                    ('ghi_chu_ngay_nhap',{'xl_title':[u'Năm sử dụng'], 'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(v)}),
                    ('ghi_chu_ban_dau',{'xl_title':[u'Ghi chú - Mô tả thêm'], 'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(v)}),
                    ('pn',{'empty_val':[u'NA','-','--'],'xl_title':[u'Mã card (P/N)']}),
                      ]
                  }),
                            
                      ]
                },#End stock.inventory.line'
                               
               u'stock.inventory.line.tkt.vtdc': {
                'title_rows':[0],
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Tổng hợp']if not self.sheet_name else [self.sheet_name]  ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                'model':'stock.inventory.line',
                'last_function':last_record_function_ltk_vtdc_,
                'last_function_for_import':last_import_function_get_self_inventory_id_,
#                 'last_function':last_record_function_get_inventory_id_,                
                'fields' : [
                    ('stt',{'func':None,'xl_title':u'STT','key':True,'required':True,'skip_field_if_not_found_column_in_some_sheet':True}),
                    ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True,
                                         'fields':[
                                                    ('name',{'set_val':'LTK Đang Chạy', 'key':True,'required': True}),
                                                     ('stock_type',{'set_val':'tram'}),
                                                    ]
                                                                        }),  
                    ('prod_lot_id_excel_readonly',{'empty_val':[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN'],'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':[u'Số serial (S/N)'],'for_excel_readonly' :True}),
                    ('barcode_for_first_read',{'empty_val':[u'NA',u"`"],'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,'xl_title':[u'Barcode'],'for_excel_readonly' :True}),
                    
                    ('product_qty', {'key':False,'set_val':1}),#'func':qty_,
                    
                    
                    ('inventory_id', {'fields':[
                                            ('name',{
#                                                 'set_val':u'LTK đang chạy ' + (self.sheet_name if self.sheet_name else '')
                                                'func':choose_inventory_id_name,
                                                'key':True,'required': True}),# coi lại
                                            ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                            ,]
                        }),
                    ('product_id',{'key':True,'required':True,
                                   'fields':[
                                            ('name',{'func':None,'xl_title':[u'Loại card'],'key':True,'required':True,'empty_val':[]}),
                                            ('type',{'set_val':'product'}),
                                            ('tracking',{'func':lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else False ,
                                                         'bypass_this_field_if_value_equal_False':True,
                                                         }),
                                            ('is_co_sn_khong_tinh_barcode',{'func':lambda val,needdata: True if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val']) !=False else False,'bypass_this_field_if_value_equal_False':True}),
                                            ('thiet_bi_id',{'fields':[('name',{'func':None,'xl_title':u'Tên hệ thống thiết bị', 'key':True,'required': True}),]}),
                                            ('categ_id',{'fields':[('name',{'func':lambda val,needdata: needdata['sheet_name'], 'key':True,'required': True}),]}),
                                            ('brand_id',{'empty_val':[u'NA'],'fields':[('name',{'func':None,'xl_title':[u'Hãng sản xuất'], 'key':True,'required': True}),]}),
                                            ('dang_chay_tao',{'set_val':True}),
                                            ('tram_ltk_tao',{'set_val':True}),
                                           
                                            ('uom_id',  { 'fields': [ #'func':uom_id_,'default':1,
                                                        ('name',{'set_val':u'Cái','key':True}),#'set_val':u'Cái',
                                                                 ('category_id', {'func': lambda n,v:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn Vị')])[0].id
                                                                                            }
                                                                     ),
                                                                           ]
                                                                }
                                             ),
                                            ]
                                   }),  
                    ('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,'xl_title':[u'Vị trí lắp đặt'], 'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('stock_type',{'set_val':'phong_may'}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True,'raise_if_False':True
                                                                                      })
                                                                   
                                                                    ]
                                                           }), 
                    ('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,'xl_title':[u'Tên tủ (Cabinet / rack)'], 'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
                                                                    ('stock_type',{'set_val':'tu'}),
                                                                   ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True,'raise_if_False':True,
                                                                                      #'fields':[('name',{'key':True,'set_val':'LTK'})]
                                                                                      })
                                                                    
                                                                    ]
                                                           }),                                           
                    ('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,'xl_title':[u'Ngăn (shelf)'], 'key':True,'required': True,'karg':{'location_type':u'Ngăn'}}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('stock_type',{'set_val':'shelf'}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True
                                                                                      #'fields':[('name',{'key':True,'set_val':'LTK'})]
                                                                                      })
                                                                    
                                                                    ]
                                                           }),         
                            
                            
                     ('location_id4',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_, 'xl_title':[u'Số thứ tự (trong shelf)'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('stock_type',{'set_val':'stt_trong_self'}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                    ]
                                                           }),  
                    ('location_id5',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_, 'xl_title':[u'Khe (Slot)'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('stock_type',{'set_val':'slot'}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':self.department_id.id,'required':True}),
                                                                    ]
                                                           }),  
                                                
                    ('location_id', {'func':lambda v,needdata: 
                        needdata['vof_dict']['location_id5']['val'] or \
                        needdata['vof_dict']['location_id4']['val'] or \
                        needdata['vof_dict']['location_id3']['val'] or \
                        needdata['vof_dict']['location_id2']['val'] or \
                        needdata['vof_dict']['location_id1']['val'] or \
                        needdata['vof_dict']['location_id_goc']['val']
                        , 'key':False}),
                    # ('pn',{'xl_title':u'Part Number','for_excel_readonly' :True}),
                    ('prod_lot_id', {'key':True,
                                      'fields':[
                                        ('name',{'func':lot_name_ ,'key':True,'required':True}),
                                        ('barcode_sn',{'func':lambda v,n:n['vof_dict']['barcode_for_first_read']['val'] ,'key':True}),
                                        ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] ,'key':True}),
                                        ('pn',{'empty_val':[u'NA','-','--'],'xl_title':[u'Mã card (P/N)']}),
                                        ('pn_id',{
                                                  'fields':[
                                                             ('name',{'empty_val':[u'NA','-','--'],'xl_title':[u'Mã card (P/N)'],'key':True, 'required':True}),
                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True  }),
                                                            ('import_location_id',{'set_val':self.import_location_id.id}),
                                                            ('dang_chay_tao',{'set_val':True}),
                                                            ('tram_ltk_tao',{'set_val':True}),
                                                            ]
                                                  }),
                                                  ('ghi_chu_ngay_nhap',{'xl_title':[u'Năm sử dụng'], 'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(v)}),
                                                  ('ghi_chu_ban_dau',{'xl_title':[u'Ghi chú - Mô tả thêm'], 'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(v)}),       
                                          ]
                                      }),
                                             ]
                                    },#End stock.inventory.line.tkbd'          
                         
                u'Thư viện công việc': {
                'inactive_include_search':True,
                'title_rows' : range(1,4), 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names':xl_workbook.sheet_names(),
                'model':'tvcv',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Công việc','key':'Both' , 'required':True } ),#'func_de_tranh_empty':lambda r:  len(r) > 2
                        ( 'loai_record',{'func':None,'set_val':u'Công Việc', 'key':False }),
                        ('department_id',{'key':True,'model':'hr.department', 'set_val':self.department_id.id,'required':True
                                                                  #'fields':[('name',{'key':True,'set_val':'LTK'})]
                                                                  }),
                        ( 'state',{'set_val':'confirmed'}),
                        ( 'cong_viec_cate_id',{'func':lambda val,needdata:get_or_create_object_sosanh(self, 'tvcvcate', {'name':needdata['sheet_name']}, {} ).id , 'key':False }),
                        ( 'code',{'func':None,'xl_title':u'Mã CV','key':True ,'require':True}),
                        ('do_phuc_tap',{'func':convert_integer,'xl_title':u'Độ phức tạp','key':False}),
                        ('diem',{'func':None,'xl_title':u'Điểm','key':False}),
                        ('don_vi',{'fields':[
                                                ('name',{'key':True, 'required':True, 'xl_title':u'Đơn vị' }),
                                                ],'key' : False, 'required' : False}),
                         ('thoi_gian_hoan_thanh',{'func':convert_integer, 'xl_title':u'Thời gian hoàn thành','key':False}),
                         ('dot_xuat_hay_dinh_ky',{'fields':[
                                                ('name',{'key':True, 'required':True,'col_index':7}),
                                                ],'key' : False,'required' : False}),  
                        ('ghi_chu',{'func':None,'xl_title':u'Ghi chú','key':False}),
                        ('children_ids',{'key':False,'required':False,
                                       'fields':[
                                                ('name',{'xl_title':u'Các công việc con',  'key':True, 'required':True, 'x2m_list':True,'skip_field_if_not_found_column_in_some_sheet':True }),
                                                ]
                                       }),  
                         ('active',{'func':lambda val, needdata: False if val ==u'na' else True,'xl_title':u'active','key':False,'skip_field_if_not_found_column_in_some_sheet':True,'use_fnc_even_cell_is_False':True}),
                      ]
                },#End stock.inventory.line'
                u'User': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': ['Sheet1'],
                'model':'res.users',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Họ và Tên','key':True,'required':True}),
                         ( 'login',{'func':None,'xl_title':u'Địa chỉ email','key':True ,'required':True}),
                        ('password',{'func':None,'required':True,'set_val':'123456'}),
                         ('lang',{'set_val':'vi_VN'}),
                         ('phone',{'func':None,'xl_title':u'Số điện thoại','key':False}),
               ('cac_sep_ids',{'key':False,'required':False,
                'fields':[
                         ('login',{'xl_title':u'Cấp trên',  'key':True, 'required':True, 'x2m_list':True}),
 
                         ]
                }),  
                 ('groups_id',{'key':False,'required':False,'skip_field_cause_first_import':self.skip_field_cause_first_import,
                'fields':[
                         ('name',{'xl_title':u'groups_id',  'key':True, 'required': True,'x2m_list':True,'remove_all_or_just_add_one_x2m':False}),     
                          ]
                }),  
                         ('job_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân viên' if v==False else v }),
                        ]
               }),  
                    ('department_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Bộ Phận',  'key':True, 'required': True}),

                         
                        ]
               }),  
                                       
                    ('partner_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['name']['val']}),
                        ('email',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['login']['val']}),
                        ('department_id',{'xl_title':None,  'key':False, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['val']}),
                         ('parent_id',{'key':False,'required':False,
                'fields':[
                         ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['fields']['name']['val'] }),
                         
                         ]
                }),  
                        
                        ]
               }),  
                      ]
                },#End stock.inventory.line'
                         
                 u'Department': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Công Ty'],
                'model':'hr.department',
                'fields' : [
                         ('name',{'func':None,'xl_title':u'công ty','key':True,'required':True}),
                         ('report_name',{'func':None,'xl_title':u'report_name','key':False,'required':False}),
                         ('short_name',{'func':None,'xl_title':u'short_name','key':False,'required':False}),
                        ('parent_id',{'fields':[('name',{'xl_title':u'parent_id','key':True,'required':True}),
                                                       ]
                                            }
                         ),
                            
                        ('cong_ty_type',{'fields':[('name',{'xl_title':u'cong_ty_type','key':True,'required':True}),
                                                       ]
                                            }
                         ),
                        ('sequence_id',{'fields':[
                            ('name',{'xl_title':None,'func':lambda v,n:n['vof_dict']['name']['val'] ,'key':True,'required':True}),
                            ('sequence_id_bbbg',{'model':'ir.sequence', 'for_excel_readonly':True,
                                                            'fields':[('name',{'xl_title':None, 'func':lambda v,n:n['vof_dict']['name']['val']+',' +'BBBG','key':True})]
                                                 }),
                            ('sequence_id_ttr',{'model':'ir.sequence', 'for_excel_readonly':True,
                                                            'fields':[('name',{'xl_title':None, 'func':lambda v,n:n['vof_dict']['name']['val']+',' +'TTR','key':True})]
                                                 }),
                                                       ]
                                            }
                         ),
                        ('default_location_id',{'fields':[
                            ('name',{'xl_title':u'default_location_id','func':None,'key':True,'required':True}),
                             ('partner_id_of_stock_for_report',{'fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                                       ]
                                            }
                         ),
                            ('is_kho_cha',{'set_val':True}),
                            ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                             ('stock_type',{'set_val':'tram'}),
                            ('department_id',
                             {'fields':[
                                 ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                                        ]
                              }),
                            ('location_id',{'fields':[('name',{'xl_title':u'location_id','key':True,'required':True}),
                                                                                  ]
                                                                       }
                                                    ),                                                                                
                                                                                ]
                                                                    }
                         ),
                            
                        ('default_location_running_id',{'model':'stock.location','fields':[
                            ('name',{'xl_title':u'default_location_id_running','func':None,'key':True,'required':True}),
                            ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                            ('is_kho_cha',{'set_val':True}),
                             ('stock_type',{'set_val':'tram'}),
                             ('partner_id_of_stock_for_report',{'model':'res.partner','fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                                       ]
                                            }
                         ),
                            ('department_id',
                             {'model':'hr.department','fields':[
                                 ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                                        ]
                              }),
                            
                            ('location_id',{'model':'stock.location', 'fields':[('name',{'xl_title':u'location_id','key':True,'required':True}),
                                                                                  ]
                                                                       }
                                                    ),                                                                                
                                                                                ]
                                                                    }
                         ),
                            
                            ('partner_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['name']['val']}),
#                         ('email',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['login']['val']}),
#                         ('department_id',{'xl_title':None,  'key':False, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['val']}),
                        ('company_type',{'xl_title':None,  'key':False, 'required': False, 'set_val':'company'}),
                        ('parent_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['parent_id']['fields']['name']['val'] }),
                        ('company_type',{'xl_title':None,  'key':False, 'required': False, 'set_val':'company'}),
#                          ('parent_id',{'key':False,'required':False,
#                                        'fields':[
#                                                 ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['fields']['parent_id']['fields']['name']['val']}),
#                                                 ]
#                                        }),  
                        ]
               }),  
                        
                        ]
               }),  
                      ]
                },#End stock.inventory.line'
                 u'location partner': {
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Location Partner'],
                'model':'stock.location',
                'fields' : [
                         ('name',{'func':None,'xl_title':u'Name','key':True,'required':True}),
                         ('usage',{'set_val':'supplier'}),
                         ('cho_phep_khac_tram_chon',{'set_val':True}),
                         ('partner_id_of_stock_for_report',{'fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                                       ]
                                            }
                         ),
                      ]
                },#End stock.inventory.line'
                
                u'Stock Location': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Location'],
                'model':'stock.location',
                'fields' : [
                         ('name',{'func':None,'xl_title':u'Tên','key':True,'required':True}),
                        ('location_id',{
                            'fields':[
                                                ('name',{'set_val':u'Kho Đài HCM','key':True,'required':True}),
                                                       ]
                                            }
                         ),
                      ]
                },#End stock.inventory.line'
                               
                u'Partner': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Partner'],
                'model':'res.partner',
                'fields' : [
                         ('stt',{'func':None,'xl_title':u'stt','key':False,'required':True,'for_excel_readonly':True}),
                         ('name',{'func':None,'xl_title':u'Tên','key':False,'required':True}),
                        ('parent_id',{
                            'fields':[
                                                ('name',{'xl_title':u'Đơn vị','key':True,'required':True}),
                                                ('company_type',{'key':False, 'required': False, 'set_val':'company'}),
                                                       ]
                                            }
                         ),
                            
                                               ('phone',{'func':None,'xl_title':u'phone','key':False, 'func': lambda v,n: int(v) if isinstance(v,float) else v}),
                                               ( 'email',{'func':None,'xl_title':u'email','key':True ,'required':True}),
                                               
                                                ('job_id',{'key':False,'required':False,
                                       'fields':[
                                                ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân Viên' if v==False else v }),
                                                ]
                                       }),  




                      ]
                }            
                                      
                }#end tag ALL_MODELS_DICT
            noti_dict = {}
            CHOOSED_MODEL_DICT = ALL_MODELS_DICT[r.type_choose]
            key_allow = CHOOSED_MODEL_DICT.get('key_allow',False)
            key_tram = key_allow and r.key_tram
            if key_allow:
                if not r.key_tram:
                    raise UserError(u'ban phai chon key_tram')
            f_ordered_a_model_dict( CHOOSED_MODEL_DICT)
            rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,CHOOSED_MODEL_DICT)
            needdata = {}
            needdata['sheet_names'] = CHOOSED_MODEL_DICT['sheet_names']
           
            sheet_names = get_key_allow(CHOOSED_MODEL_DICT, 'sheet_names', key_tram)
            if callable(sheet_names):
                sheet_names = sheet_names(self)
            for sheet_name in sheet_names:
                print ('sheet_name',sheet_name)
                MODEL_DICT = deepcopy(CHOOSED_MODEL_DICT)
                needdata['sheet_name'] = sheet_name
#                 needdata['self'] = self
                sheet = xl_workbook.sheet_by_name(sheet_name)
                row_title_index =None
                
                title_rows = MODEL_DICT.get('title_rows_some_sheets',{}).get(sheet_name)
                title_rows = title_rows or get_key_allow(CHOOSED_MODEL_DICT, 'title_rows', key_tram)  # MODEL_DICT['title_rows']
                for row in title_rows:
                    for col in range(0,sheet.ncols):
                        if VERSION_INFO ==2:
                            value_may_be_title = unicode(sheet.cell_value(row,col))
                        else:
                            value_may_be_title = str(sheet.cell_value(row,col))
                        is_map_xl_title = lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE( MODEL_DICT, value_may_be_title, col,key_tram)
                        if is_map_xl_title:
                            row_title_index = row
                        if row ==4:
                            print ('is_map_xl_title',is_map_xl_title)
                            if is_map_xl_title:
                                print ('***is_map_xl_title == True khi row == 4')
                print ('MODEL_DICT',MODEL_DICT)
                merge_tuple_list =  sheet.merged_cells
                if row_title_index == None:
                    raise UserError(u'row_title_index == None, không có xl_title nào match với excel')
                
                off_set_row = CHOOSED_MODEL_DICT.get('begin_data_row_offset_with_title_row',1)
                print ('***row_title_index***',row_title_index)
                min_row = row_title_index + off_set_row
                first_row = min_row + self.begin_row
                if not self.dong_test:
                    last_row = sheet.nrows
                else:
                    last_row = first_row + self.dong_test
                if last_row >sheet.nrows:
                    last_row =  sheet.nrows
                if first_row >  last_row :
                    raise UserError(u'first_row >  last_row')
                print ("(first_row, last_row)",(first_row, last_row))
                
                for c,row in enumerate(range(first_row, last_row)):
                    print ('row',row)
                    create_instance( self, MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,
                                      main_call_create_instance=CHOOSED_MODEL_DICT['model'],key_tram=key_tram)
            if c:
                r.imported_number_of_row = c + 1
            last_function_for_import  = CHOOSED_MODEL_DICT.get('last_function_for_import')
            if last_function_for_import:
                last_function_for_import()
            r.log= noti_dict
            

            

