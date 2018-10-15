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
import xlwt
_logger = logging.getLogger(__name__)
from odoo.osv import expression
import sys
VERSION_INFO   = sys.version_info[0]
from collections import  OrderedDict
from odoo.addons.dai_tgg.models.model_dict import gen_model_dict
# from odoo.addons.dai_tgg.models.model_dict import ALL_MODELS_DICT
from xlutils.copy import copy
# from odoo.addons.tonkho.controllers.controllers import  get_width



def get_width(num_characters):
    return int((1+num_characters) * 256)
not_horiz_center_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align: wrap on , vert centre; borders: left thin,right thin, top thin, bottom thin")
header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ; align:  vert centre;  pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
def get_or_create_object_has_x2m (self, class_name, search_dict,
                                write_dict ={},
                                is_must_update=False, 
                                noti_dict=None,
                                inactive_include_search = False, x2m_field=False,remove_all_or_just_add_one_x2m = True,
                                is_return_get_or_create = True,
#                                  not_update_field_if_instance_exist_list=[],
#                                  dict_get_or_create_para_all_field={},
                                 model_dict = {},
                                 key_tram =  None,
                                 not_create = False
                                 ):
    
    if x2m_field:
        x2m_values = search_dict[x2m_field]
        result = []
        for val in x2m_values:
            search_dict[x2m_field] = val #
            object, get_or_create = get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search,is_return_get_or_create=True,
#                                     not_update_field_if_instance_exist_list=not_update_field_if_instance_exist_list,
#                                     dict_get_or_create_para_all_field = dict_get_or_create_para_all_field,
                                    model_dict = model_dict,
                                    key_tram = key_tram,
                                    not_create = not_create
                                    )
            result.append(object.id)
        if remove_all_or_just_add_one_x2m == True:
            six_or_zero = 6
#             obj_id =  [(six_or_zero,False,result)]
        else:
            six_or_zero = 4
        obj_id =  [(six_or_zero,result[0],False)]
    else:
        obj, get_or_create =  get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search, is_return_get_or_create=True,
#                                     not_update_field_if_instance_exist_list=not_update_field_if_instance_exist_list,
#                                     dict_get_or_create_para_all_field = dict_get_or_create_para_all_field,
                                    model_dict = model_dict,
                                    key_tram = key_tram,
                                    not_create = not_create
                                    )
        if obj != False:
            obj_id = obj.id
        else:
            obj_id = False
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
                                key_tram = None,
                                not_create = False                              
                                ):
    
    search_dict_new = {}
    write_dict_new = {}
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
    else:
        this_model_noti_dict = None
    if inactive_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
    domain = []
    for f_name in search_dict:
        field_attr = model_dict['fields'][f_name]
        val =  search_dict[f_name]
#         get_or_create_para = field_attr.get('get_or_create_para',{})
       
        f_name = get_key_allow(field_attr, 'transfer_name', key_tram) or f_name
        get_or_create_para = get_key_allow(field_attr, 'get_or_create_para', key_tram, {})
        operator_search = get_or_create_para.get('operator_search','=')
       
        tuple_in = (f_name, operator_search, val)
        domain.append(tuple_in)
        search_dict_new[f_name] =  val
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
#         search_dict.update(write_dict)
        for f_name,val in write_dict.items():
            field_attr = model_dict['fields'][f_name]
            f_name = get_key_allow(field_attr, 'transfer_name', key_tram) or f_name
            search_dict_new[f_name]=val
        if not not_create:
            created_object = self.env[class_name].create(search_dict_new)
            if this_model_noti_dict !=None:
                this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
        else:
            created_object = False
        
        return_obj =  created_object
    else:
        for f_name,val in write_dict.items():
            field_attr = model_dict['fields'][f_name]
            f_name = get_key_allow(field_attr, 'transfer_name', key_tram) or f_name
            get_or_create_para = get_key_allow(field_attr, 'get_or_create_para', key_tram, {})
            not_update_field_if_instance_exist = get_or_create_para.get('not_update_field_if_instance_exist',False)
            if not not_update_field_if_instance_exist or (not_update_field_if_instance_exist and not getattr(searched_object, f_name)) :
                write_dict_new[f_name] = val
      
        if not is_must_update:
            is_write = False
            for f_name in write_dict_new:
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
            if not not_create:
                searched_object.write(write_dict_new)
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
    
def empty_string_to_False(readed_value):
    if VERSION_INFO==2:
        check_str = isinstance(readed_value,unicode) or isinstance(readed_value,str)
    else:
        check_str =  isinstance(readed_value,str)
    
    if check_str :
        if readed_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_value)
        if not rs:
            return False
    return readed_value
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

def write_get_or_create_title(model_dict,sheet,sheet_of_copy_wb,title_row,key_tram):
    fields = model_dict['fields']
#     print ('fields',fields)
    for fname,attr in fields.items():
        childrend_model_dict =  attr
        childrend_fields = childrend_model_dict.get('fields')
        if childrend_fields:
            write_get_or_create_title(childrend_model_dict,sheet,sheet_of_copy_wb,title_row,key_tram)
        offset_write_xl = get_key_allow(attr, 'offset_write_xl', key_tram,None)
        if offset_write_xl !=None:
            col = sheet.ncols + offset_write_xl 
            title = fname + ' get_or_create'
            sheet_of_copy_wb.col(col).width =  get_width(len(title))
            sheet_of_copy_wb.write(title_row, col,title ,header_bold_style)
    
    
    
    
def f_ordered_a_model_dict(model_dict):
    fields = model_dict['fields']
#     print ('fields',fields)
    for fname,attr in fields:
        childrend_model_dict=  attr
        childrend_fields = childrend_model_dict.get('fields')
        if childrend_fields:
            new_ordered_dict = f_ordered_a_model_dict(childrend_model_dict)
    model_dict['fields']=OrderedDict(fields)
def rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,MODEL_DICT,key_tram=False):
    print ('in rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR...')
#     model_name = MODEL_DICT['model']
    model_name = get_key_allow(MODEL_DICT, 'model', key_tram)
    fields= self.env[model_name]._fields
    for field_tuple in MODEL_DICT.get('fields',{}).items():
        f_name = field_tuple[0]
        field_attr = field_tuple[1]
        f_name = get_key_allow(field_attr, 'transfer_name', key_tram) or  f_name
        skip_this_field = get_key_allow(field_attr, 'skip_this_field', key_tram,False)
        if  (not field_attr.get('for_excel_readonly') and not skip_this_field) and (f_name not in fields )  :
            raise UserError(u'field %s không có trong  danh sách fields của model %s'%(f_name,model_name))
#         if field_attr.get('xl_title'):
#                 field_attr[ 'xl_title_unidecode'] = unidecode(field_attr[u'xl_title'])
#         if f_name =='thiet_bi_id_ltk':
#             raise UserError ("not field_attr.get('for_excel_readonly') and  not skip_this_field %s -skip_this_field:%s - field_attr.get('for_excel_readonly') %s " % (not field_attr.get('for_excel_readonly') and  not skip_this_field,skip_this_field,field_attr.get('for_excel_readonly') ))
        if not field_attr.get('for_excel_readonly') and  not skip_this_field:# and not skip_this_field
#             if f_name =='thiet_bi_id_ltk':
#                 print ('kakak')
            field = fields[f_name]
            field_attr['field_type'] = field.type
            if field.comodel_name:
                field_attr['model'] = field.comodel_name
                rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,field_attr,key_tram=key_tram)
        elif 'model' in field_attr:
                rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,field_attr,key_tram=key_tram)
def get_key_allow(field_attr, attr, key_tram,default_if_not_attr=None):
    value = field_attr.get(attr,default_if_not_attr)
    if isinstance(value, dict) and key_tram:
        value =  value.get(key_tram,default_if_not_attr) if key_tram in value else value.get('all_key_tram',default_if_not_attr)
    return value
    


def lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE(MODEL_DICT, read_excel_value_may_be_title, col,key_tram):
    #print 'read_excel_value_may_be_title',read_excel_value_may_be_title
#     if read_excel_value_may_be_title ==u'Ngăn':
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
            is_real_xl_match_with_xl_excel = lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE(field_attr, read_excel_value_may_be_title, col,key_tram)
        elif xl_title:
            if isinstance(xl_title, list):
                xl_title_s = xl_title
            else:
                xl_title_s = [xl_title]
            for xl_title in xl_title_s:
#                 is_map = xl_title == read_excel_value_may_be_title
#                 is_map = re.search(u'^'+xl_title+u'$',read_excel_value_may_be_title)
                is_map = re.search(xl_title,read_excel_value_may_be_title,re.IGNORECASE)
                if is_map:
                    field_attr['col_index'] = col
                    is_real_xl_match_with_xl_excel = True        
        is_map_xl_title = is_map_xl_title or is_real_xl_match_with_xl_excel
    return is_map_xl_title #or is_map_xl_title_foreinkey

def create_instance (self, MODEL_DICT, sheet, row, merge_tuple_list,needdata, noti_dict, main_call_create_instance_model = False,
                    key_tram=None, 
                    not_create = False,
                    workbook_copy = False,
                    sheet_of_copy_wb = False,
                     ):
    key_search_dict = {}
    update_dict = {}
    vof_dict = {} # value of fields of one instance
    model_name = get_key_allow(MODEL_DICT, 'model', key_tram)
    
    
    if model_name ==None:
        raise UserError(u'key_tram:%s-%s'%(key_tram,str(MODEL_DICT)))
    if main_call_create_instance_model:
        needdata['vof_dict'] = vof_dict
    x2m_fields = []
    remove_all_or_just_add_one_x2m = True
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    for field_name,field_attr  in MODEL_DICT['fields'].items():
        if get_key_allow(field_attr, 'skip_this_field', key_tram, False):
            continue
        col_index = get_key_allow(field_attr, 'col_index', key_tram, None)
        val = False
        
        xl_title = get_key_allow(field_attr, 'xl_title', key_tram)#moi them , moi bo field_attr.get('xl_title')
       
        ###  deal set_val ########
        set_val = get_key_allow( field_attr,'set_val',key_tram)
        if callable(set_val):
                set_val = set_val(self)
        ###  !deal set_val ########
        
        
        
        ## check match bw xl_title vs real xl
        
        if set_val ==None:
            if col_index == None and xl_title:
                is_match =  False
            else:
                is_match = True
            if not is_match :
                sheet_allow_this_field_not_has_exel_col =get_key_allow( field_attr,'sheet_allow_this_field_not_has_exel_col',key_tram)
                skip_field_if_not_found_column_in_some_sheet = get_key_allow(field_attr,'skip_field_if_not_found_column_in_some_sheet',key_tram)
                allow_not_match =  skip_field_if_not_found_column_in_some_sheet or (sheet_allow_this_field_not_has_exel_col and needdata['sheet_name'] in sheet_allow_this_field_not_has_exel_col)
                if not allow_not_match:
                    raise UserError(u'có khai báo xl_title nhưng không match với file excel, field: %s, xl_title: %s, dòng: %s ' %(field_name,field_attr.get('xl_title'),row))
        ##!!! check match bw xl_title vs real xl
        
        a_field_vof_dict = vof_dict.setdefault(field_name,{})
        
        ### deal skip_field_cause_first_import####
        skip_field_cause_first_import = get_key_allow(field_attr, 'skip_field_cause_first_import', key_tram)
        if callable(skip_field_cause_first_import):
            skip_field_cause_first_import = skip_field_cause_first_import(self)
        ### end  deal skip_field_cause_first_import####
        
        
        if set_val != None:
            val = set_val
        elif skip_field_cause_first_import:
            continue
        elif col_index !=None: # đọc file exc
            xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
            a_field_vof_dict['excel_val'] = xl_val
            val = empty_string_to_False(xl_val)
            field_type_of_this_model = MODEL_DICT.get('field_type')
            if val != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('is_x2m_field'):
                val = val.split(',')
                val = map(lambda i: i.strip(),val)
        elif field_attr.get('fields') :
            val, vof_dict_childrend, get_or_create  = create_instance (self, field_attr, sheet, row, merge_tuple_list, needdata, noti_dict,key_tram=key_tram, 
                                                                       not_create = not_create,
                                                                       workbook_copy = workbook_copy,
                                                                       sheet_of_copy_wb = sheet_of_copy_wb
                                                                       )
            a_field_vof_dict['fields'] = vof_dict_childrend
            a_field_vof_dict['get_or_create'] = get_or_create
            
            if not_create:
                offset_write_xl = get_key_allow(field_attr, 'offset_write_xl', key_tram,None)
            else:
                offset_write_xl =  None
            if offset_write_xl !=None:
                get_or_create_display = u'Đã Có' if get_or_create else u'Chưa'
                sheet_of_copy_wb.write(row,sheet.ncols + offset_write_xl , get_or_create_display,not_horiz_center_border_style)
        
        
        a_field_vof_dict['before_func_val'] = val
        func = get_key_allow( field_attr,'func',key_tram)
        karg = get_key_allow( field_attr,'karg',key_tram,{})
        if func:
            try:
                val = func(val, needdata,**karg)
            except TypeError:
                val = func(val, needdata,self,**karg)
        
        #### deal replace string ####
        replace_string = get_key_allow( field_attr,'replace_string',key_tram)
        if  replace_string and check_is_string_depend_python_version(val):
            for pattern,repl in replace_string:
                val = re.sub(pattern, repl, val)
        #### end  deal replace string ####
        
        #### deal empty val ###
        empty_val = get_key_allow( field_attr,'empty_val',key_tram)
        if empty_val and val in empty_val:
            val = False   
        #### !!!deal empty val ###
        
        
        
        
        #### deal  replace val#####
        replace_val = get_key_allow( field_attr,'replace_val',key_tram)
        if replace_val:
            replace_val_tuple = replace_val.get(needdata['sheet_name']) or replace_val.get('all')
            if replace_val_tuple:
                for k,v in replace_val_tuple:
                    if val ==k:
                        val = v
                        break
        #### !!!deal  replace val#####
                    
                    
                    
        if val == False and  field_attr.get('default'):
            val = field_attr.get('default')
        a_field_vof_dict['val'] = val
       
        if not_create:     
            required  = get_key_allow(field_attr, 'required',key_tram + '_not_create', False)     
        else:
            required =get_key_allow(field_attr, 'required',key_tram, False)       
       
        bypass_this_field_if_value_equal_False = get_key_allow(field_attr, 'bypass_this_field_if_value_equal_False', key_tram, False)
        if required and val==False:
            if field_attr.get('raise_if_False'):
                raise UserError('raise_if_False field: %s'%field_name)
            if main_call_create_instance_model:
                print ('skip because required, field %s'%field_name)
            get_or_create = False
            return val ,vof_dict, get_or_create
        elif bypass_this_field_if_value_equal_False and val==False:
            continue
        elif not field_attr.get('for_excel_readonly'):
            key_or_not = field_attr.get('key')
            if key_or_not==True:
                key_search_dict [field_name] = val
            elif key_or_not == 'Both':
                key_search_dict [field_name] = val
                update_dict [field_name] = val
            else:
                update_dict [field_name] = val
#         print ('4',count)
        if field_attr.get('is_x2m_field'):
                x2m_fields.append(field_name)
                remove_all_or_just_add_one_x2m &= field_attr.get('remove_all_or_just_add_one_x2m',True)
                
    
    last_record_function = get_key_allow(MODEL_DICT, 'last_record_function', key_tram)
    if last_record_function:
        last_record_function(needdata)
    get_or_create = False
    if key_search_dict:
        obj_val, get_or_create = get_or_create_object_has_x2m(self, model_name, key_search_dict, update_dict,
                                is_must_update = True, 
                                noti_dict = noti_dict,
                                inactive_include_search  = inactive_include_search, 
                                x2m_field = x2m_fields[0] if x2m_fields else False,
                                remove_all_or_just_add_one_x2m=remove_all_or_just_add_one_x2m,
                                is_return_get_or_create = True,
                                model_dict=MODEL_DICT,
                                key_tram = key_tram,
                                not_create = not_create
                                )
        if main_call_create_instance_model:
            print ('get_or_create',get_or_create)
    else:
        obj_val = False
        if main_call_create_instance_model: 
            print ('no get or create because no key_search_dict ')
    return obj_val, vof_dict, get_or_create
def define_col_index(title_rows,sheet,COPY_MODEL_DICT,key_tram):
    read_excel_value_may_be_titles = []
    titles = []
    row_title_index =None
    for row in title_rows:
        for col in range(0,sheet.ncols):
            
            if VERSION_INFO ==2:
                read_excel_value_may_be_title = unicode(sheet.cell_value(row,col))
            else:
                read_excel_value_may_be_title = str(sheet.cell_value(row,col))
            is_map_xl_title = lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE( COPY_MODEL_DICT, read_excel_value_may_be_title, col,key_tram)
            read_excel_value_may_be_titles.append(read_excel_value_may_be_title)
            
            if is_map_xl_title:
                row_title_index = row
                titles.append(read_excel_value_may_be_title)
    print ( 'read_excel_value_may_be_titles*******',read_excel_value_may_be_titles)
    print ('**titles',titles)
    return row_title_index
    
def importthuvien(odoo_or_self_of_wizard,import_for_stock_tranfer = False,key=False,key_tram=False,
                  not_create = False):
    if not import_for_stock_tranfer:
        ALL_MODELS_DICT = gen_model_dict()
    else:
        ALL_MODELS_DICT =  import_for_stock_tranfer
    self = odoo_or_self_of_wizard
#     for r in self:
    file_content = base64.decodestring(self.file)
    xl_workbook = xlrd.open_workbook(file_contents = file_content, formatting_info=True)
    noti_dict = {}
    if not import_for_stock_tranfer:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[self.type_choose]
    else:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[key]
    key_allow = CHOOSED_MODEL_DICT.get('key_allow',False)
    self_key_tram =  getattr(self,'key_tram',False) or key_tram
    key_tram = key_allow and self_key_tram
    if key_allow and not key_tram:
        raise UserError(u'ban phai chon key_tram')
    f_ordered_a_model_dict( CHOOSED_MODEL_DICT)
    rECURSIVE_ADD_MODEL_NAME_TO_FIELD_ATTR(self,CHOOSED_MODEL_DICT,key_tram=key_tram)
    needdata = {}
    sheet_names = get_key_allow(CHOOSED_MODEL_DICT, 'sheet_names', key_tram)
    if callable(sheet_names):
        sheet_names = sheet_names(self)
    needdata['sheet_names'] = sheet_names
    
    ### moi them
    not_create = get_key_allow(CHOOSED_MODEL_DICT, 'not_create', key_tram) or not_create
    if not_create:
        workbook_copy = copy(xl_workbook)
    else:
        workbook_copy = None
    ### end moi them  
        
    for sheet_name in sheet_names:
        COPY_MODEL_DICT = deepcopy(CHOOSED_MODEL_DICT)
        needdata['sheet_name'] = sheet_name
        sheet = xl_workbook.sheet_by_name(sheet_name)
        # moi them:
        if not_create:
#             sheet_of_copy_wb = workbook_copy.sheet_by_name(sheet_name)#AttributeError: 'PatchedWorkbook' object has no attribute 'sheet_by_name'
            sheet_of_copy_wb = workbook_copy.get_sheet(0)
        else:
            sheet_of_copy_wb = False
        title_rows = CHOOSED_MODEL_DICT.get('title_rows_some_sheets',{}).get(sheet_name)
        title_rows = title_rows or get_key_allow(CHOOSED_MODEL_DICT, 'title_rows', key_tram)  # MODEL_DICT['title_rows']
#         ncols = sheet.ncols
        row_title_index = define_col_index(title_rows,sheet,COPY_MODEL_DICT,key_tram)
        merge_tuple_list =  sheet.merged_cells
        print ('merge_tuple_list',merge_tuple_list)
        if row_title_index == None:
            raise UserError(u'row_title_index == None, không có xl_title nào match với excel')
        if not_create:
            write_get_or_create_title(CHOOSED_MODEL_DICT,sheet,sheet_of_copy_wb,row_title_index,key_tram)
        off_set_row = get_key_allow(CHOOSED_MODEL_DICT, 'begin_data_row_offset_with_title_row', key_tram, 1)
#         off_set_row = CHOOSED_MODEL_DICT.get('begin_data_row_offset_with_title_row',1)
        min_row = row_title_index + off_set_row
        first_row = min_row + getattr(self,'begin_row',0)
        if not getattr(self,'dong_test',None):
            last_row = sheet.nrows
        else:
            last_row = first_row + self.dong_test
        if last_row >sheet.nrows:
            last_row =  sheet.nrows
        if first_row >  last_row :
            raise UserError(u'first_row >  last_row')
        for c,row in enumerate(range(first_row, last_row)):
            print ('sheet_name',sheet_name,'row',row)
            create_instance( self, COPY_MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,
                              main_call_create_instance_model=True,
                              key_tram=key_tram,
                              not_create = not_create,
                              workbook_copy = workbook_copy,
                              sheet_of_copy_wb = sheet_of_copy_wb,
                               )
    if c:
        self.imported_number_of_row = c + 1
    last_import_function  = get_key_allow(CHOOSED_MODEL_DICT,'last_import_function',key_tram)
    if last_import_function:
        last_import_function(needdata,self)
    self.log= noti_dict
    return workbook_copy
    
            

            

