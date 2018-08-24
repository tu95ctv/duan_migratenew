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
# from odoo.addons.dai_tgg.models.model_dict import ALL_MODELS_DICT

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
            field_attr = model_dict['fields'][f_name]
            get_or_create_para = get_key_allow(field_attr, 'get_or_create_para', key_tram, {})
            not_update_field_if_instance_exist = get_or_create_para.get('not_update_field_if_instance_exist',False)
            if not not_update_field_if_instance_exist or (not_update_field_if_instance_exist and not getattr(searched_object, f_name)) :
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
                except:
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
    print ('fields',fields)
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
        value =  value.get(key_tram,default_if_not_attr) if key_tram in value else value.get('all_key_tram',default_if_not_attr)
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
#         raise UserError(u'aka Ngăn')
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
        set_val = get_key_allow( field_attr,'set_val',key_tram)
        if callable(set_val):
                set_val = set_val(self)
        if col_index == None and xl_title:
            is_match =  False
        else:
            is_match = True
        if not is_match  and set_val ==None:
            sheet_allow_this_field_not_has_exel_col =get_key_allow( field_attr,'sheet_allow_this_field_not_has_exel_col',key_tram)
            skip_field_if_not_found_column_in_some_sheet = get_key_allow(field_attr,'skip_field_if_not_found_column_in_some_sheet',key_tram)
            allow_not_match =  skip_field_if_not_found_column_in_some_sheet or (sheet_allow_this_field_not_has_exel_col and needdata['sheet_name'] in sheet_allow_this_field_not_has_exel_col)
            if not allow_not_match:
                raise UserError(u'có khai báo xl_title nhưng không match với file excel, field: %s, xl_title: %s, dòng: %s ' %(field_name,field_attr.get('xl_title'),row))
        avof_dict = vof_dict.setdefault(field_name,{})
        
        
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
        
        elif field_attr.get('fields') :
            xl_val, vof_dict_childrend, get_or_create  = create_instance (self, field_attr, sheet, row, merge_tuple_list, needdata, noti_dict,key_tram=key_tram)
            avof_dict['fields'] = vof_dict_childrend
            avof_dict['get_or_create'] = get_or_create

        avof_dict['before_func_val'] = xl_val
        
        
        func = get_key_allow( field_attr,'func',key_tram)
        print ("key_tram",key_tram)
        karg = get_key_allow( field_attr,'karg',key_tram,{})
        print ('func',func)
        
        if func:
            try:
                xl_val = func(xl_val, needdata,**karg)
            except TypeError:
                xl_val = func(xl_val, needdata,self,**karg)
            
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
        bypass_this_field_if_value_equal_False = get_key_allow(field_attr, 'bypass_this_field_if_value_equal_False', key_tram, True)
        if required and xl_val==False:
            if field_attr.get('raise_if_False'):
                raise UserError('raise_if_False field: %s'%field_name)
            return False , vof_dict,False
        elif bypass_this_field_if_value_equal_False and xl_val==False:
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
def importthuvien(odoo_or_self_of_wizard,ALL_MODELS_DICT):
    self = odoo_or_self_of_wizard
#     for r in self:
    recordlist = base64.decodestring(self.file)
    xl_workbook = xlrd.open_workbook(file_contents = recordlist)
    noti_dict = {}
    CHOOSED_MODEL_DICT = ALL_MODELS_DICT[self.type_choose]
    key_allow = CHOOSED_MODEL_DICT.get('key_allow',False)
    key_tram = key_allow and self.key_tram
    if key_allow and not self.key_tram:
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
        for c,row in enumerate(range(first_row, last_row)):
            print ('row',row)
            create_instance( self, MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,
                              main_call_create_instance=CHOOSED_MODEL_DICT['model'],key_tram=key_tram)
    if c:
        self.imported_number_of_row = c + 1
    last_function_for_import  = CHOOSED_MODEL_DICT.get('last_function_for_import')
    if last_function_for_import:
        last_function_for_import(needdata,self)
    self.log= noti_dict
            

            

