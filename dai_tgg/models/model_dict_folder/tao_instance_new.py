 # -*- coding: utf-8 -*-
import re
import xlrd
# import time
# from unidecode import unidecode
# import xlwt
# from collections import  OrderedDict
# import operator


from odoo.exceptions import UserError
import base64
from copy import deepcopy


# import sys
# VERSION_INFO   = sys.version_info[0]

from odoo.addons.dai_tgg.models.model_dict_folder.model_dict import gen_model_dict
# from odoo.addons.dai_tgg.models.model_dict import ALL_MODELS_DICT
from xlutils.copy import copy
# from odoo.addons.tonkho.controllers.controllers import  get_width




### new ##


from odoo.addons.dai_tgg.models.model_dict_folder.tool_tao_instance import not_horiz_center_border_style,read_excel_cho_field,check_is_string_depend_python_version,empty_string_to_False,get_key_allow#,get_width,header_bold_style,VERSION_INFO
from odoo.addons.dai_tgg.models.model_dict_folder.get_or_create_func import get_or_create_object_has_x2m
from odoo.addons.dai_tgg.models.model_dict_folder.recursive_func import muon_xuat_dac_tinh_gi,ordered_a_model_dict,recursive_add_model_name_to_field_attr,define_col_index,define_col_index,check_xem_att_co_nam_ngoai_khong,write_get_or_create_title,check_col_index_match_xl_title
# from odoo.addons.dai_tgg.models.model_dict_folder.recursive_func import tim_type_cua_attr
MAP_TYPE = {
                      'integer':int,
                      'float':float, 
                      'many2one':int,
                      'char':str,
                      'selection':str,
                      'text':str, 
                      'boolean':bool,
                      'many2many':list,
                      'one2many':list
                      }

# def check_type(val,field_type):
#     if val != False:
#         try:
#             class_or_type_or_tuple = MAP_TYPE[field_type]
#         except:
#             raise UserError('')
#         isinstance(object, class_or_type_or_tuple)

#####################vkjzkldjfklsdjfkldsjf
def replace_val_for_ci(field_attr,key_tram,val,needdata):
    
    
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
                
    ### deal defautl ###
    if val == False and  field_attr.get('default'):
        val = field_attr.get('default')
    
    ### !!!!deal defautl ###
    return val
def check_type_of_val(field_attr,val,field_name,model_name):        
    field_type = field_attr.get('field_type')
    if field_type:
        type_allow = field_attr.get('type_allow',[])
        if val != False:
            try:
                class_or_type_or_tuple = MAP_TYPE[field_type]
            except:
                raise UserError(u'không có field_type:%s này'%field_type)
            if field_attr.get('is_x2m_field'):
                class_or_type_or_tuple = list
            type_allow.append(class_or_type_or_tuple)
            pass_type_check = False
            for a_type_allow in type_allow:
                if isinstance(val, a_type_allow):
                    pass_type_check = True
            if not pass_type_check:
                raise UserError(u'model: %s- field:%s có giá trị: %s, đáng lẽ là field_type:%s nhưng lại có type %s'%(model_name, field_name,val,field_type,type(val)))
#     else:
#         raise UserError(u'Không có field_type:%s trong biến MAP_TYPE'%(field_type))      
def read_val_for_ci(self,set_val,col_index,a_field_vof_dict,MODEL_DICT,field_attr,sheet,row,
                    merge_tuple_list,not_create,needdata,noti_dict,key_tram,workbook_copy,sheet_of_copy_wb
                    ):  
    
    ### end  deal skip_field_cause_first_import####
    val = False
    field_type_of_this_model = MODEL_DICT.get('field_type')
    if set_val != None:
        val = set_val
    elif col_index !=None: # đọc file exc
        xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
        a_field_vof_dict['excel_val'] = xl_val
        val = empty_string_to_False(xl_val)
        if val != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('is_x2m_field'):
            val = val.split(',')
            val = list(map(lambda i: i.strip(),val))
    elif field_attr.get('fields') :
        val, get_or_create  = create_instance (self, field_attr, sheet, row, merge_tuple_list, needdata, noti_dict,key_tram=key_tram, 
                                                                   not_create = not_create,
                                                                   workbook_copy = workbook_copy,
                                                                   sheet_of_copy_wb = sheet_of_copy_wb
                                                                   )
#             a_field_vof_dict['fields'] = vof_dict_childrend
        a_field_vof_dict['get_or_create'] = get_or_create
        vof_dict_childrend = field_attr['fields']
        if not_create:
            offset_write_xl = get_key_allow(field_attr, 'offset_write_xl', key_tram,None)
            if offset_write_xl !=None:
                if get_or_create:
                    get_or_create_display = u'Đã Có' 
                else:
                    if vof_dict_childrend['name']['val'] !=False:
                        get_or_create_display = u'Chưa'
                    else:
                        get_or_create_display = u'empty cell'
                sheet_of_copy_wb.write(row,sheet.ncols + offset_write_xl , get_or_create_display,not_horiz_center_border_style)
    return val       
     
                    
def in_for_create_instance(self,field_name,field_attr,key_tram,needdata,row,sheet,
                           MODEL_DICT,not_create,workbook_copy,sheet_of_copy_wb,
                           merge_tuple_list,model_name,main_call_create_instance_model,noti_dict,
                           key_search_dict,update_dict,x2m_fields,some_dict):
#     instance_false = False
    skip_this_field = get_key_allow(field_attr, 'skip_this_field', key_tram, False)
    if callable(skip_this_field):
            skip_this_field = skip_this_field(self)
    if skip_this_field:
            return 'continue'
    col_index = get_key_allow(field_attr, 'col_index', key_tram, None)
    a_field_vof_dict = field_attr # them 3
    ###  deal set_val ########
    set_val = get_key_allow( field_attr,'set_val',key_tram)
    func = get_key_allow( field_attr,'func',key_tram)
    val = read_val_for_ci(self,set_val,col_index,a_field_vof_dict,MODEL_DICT,field_attr,sheet,row,
                    merge_tuple_list,not_create,needdata,noti_dict,key_tram,workbook_copy,sheet_of_copy_wb
                    )
    a_field_vof_dict['before_func_val'] = val
    # func
    karg = get_key_allow( field_attr,'karg',key_tram,{})
    if karg ==None:
        karg ={}
    if func:
        try:
            val = func(val, needdata,**karg)
        except TypeError:
            val = func(val, needdata,self,**karg)
    #end func
    val =replace_val_for_ci(field_attr,key_tram,val,needdata)
    check_type_of_val(field_attr,val,field_name,model_name)
    a_field_vof_dict['val'] = val
    print ("row", row,'model_name',model_name,'field', field_name, 'val', val)
    
    
    bypass_this_field_if_value_equal_False = get_key_allow(field_attr, 'bypass_this_field_if_value_equal_False', key_tram, False)
    if not_create:     
        required   = get_key_allow(field_attr, 'required',key_tram + '_not_create', False)     
        
        real_required_for_not_create_mode  = get_key_allow(field_attr, 'required',key_tram, False)   
        
        if bypass_this_field_if_value_equal_False:
            real_required_for_not_create_mode = False
        else:
            real_required_for_not_create_mode = real_required_for_not_create_mode
        if real_required_for_not_create_mode and val==False:
            some_dict['instance_false'] = True
    else:
        required = get_key_allow(field_attr, 'required',key_tram, False)  
       
        if bypass_this_field_if_value_equal_False:
            required = False
        else:
            required = required
        required = required and not bypass_this_field_if_value_equal_False
            
    #### !!! deal required #####    
    
    
    
    if  bypass_this_field_if_value_equal_False and val==False:
        return 'continue'
    elif required and val==False:
        if field_attr.get('raise_if_False'):
            raise UserError('raise_if_False field: %s'%field_name)
        if main_call_create_instance_model:
            print ('skip because required,model %s- field %s'%(model_name,field_name))
            noti_dict['skip because required'] +=  1
        return 'break' #sua 5
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
            some_dict['remove_all_or_just_add_one_x2m'] &= field_attr.get('remove_all_or_just_add_one_x2m',True)
#     return instance_false
    return False        
def get_or_create_instance(self,
                           model_name,
                           key_search_dict,
                           update_dict,
                           not_create,
                           instance_false,
                           noti_dict,
                           inactive_include_search,
                           x2m_fields,
                           remove_all_or_just_add_one_x2m,MODEL_DICT,key_tram):
    if key_search_dict:
        if not_create:
            if instance_false:
                obj_val = False
                get_or_create = False
                return obj_val, get_or_create
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
        return obj_val, get_or_create 
    else:
        raise UserError(u' không có key_search_dict')               

################# CREATE INSTANCE
def create_instance (self, MODEL_DICT, sheet, row, merge_tuple_list,needdata, noti_dict, main_call_create_instance_model = False,
                    key_tram=None, 
                    not_create = False,
                    workbook_copy = False,
                    sheet_of_copy_wb = False,
                    some_var_para = {}
                     ):
    key_search_dict = {}
    update_dict = {}
    model_name = get_key_allow(MODEL_DICT, 'model', key_tram)
#     if main_call_create_instance_model:
#         needdata['vof_dict'] = MODEL_DICT.get('fields')   #sua 2   vof_dict
#     
    
    x2m_fields = []
#     remove_all_or_just_add_one_x2m = True
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    some_dict = {'instance_false':False,'remove_all_or_just_add_one_x2m':True}
    break_condition = False
    for field_name,field_attr  in MODEL_DICT['fields'].items():
        code = in_for_create_instance(self,field_name,field_attr,key_tram,needdata,row,sheet,
                           MODEL_DICT,not_create,workbook_copy,sheet_of_copy_wb,
                           merge_tuple_list,model_name,main_call_create_instance_model,noti_dict,
                           key_search_dict,update_dict,x2m_fields,some_dict)
        if code =='break':
#             return obj,get_or_create
            break_condition = True# moi them
            break
    if break_condition:
        if main_call_create_instance_model:
            if  True:#getattr(self, 'allow_cate_for_ghi_chu',False):
                break_condition_func_for_main_instance = some_var_para.get('break_condition_func_for_main_instance',None)
                if break_condition_func_for_main_instance:
                    break_condition_func_for_main_instance(needdata)
        obj_val = False
        get_or_create = False
        return obj_val,get_or_create
    
    
    
    last_record_function = get_key_allow(MODEL_DICT, 'last_record_function', key_tram)
    if last_record_function:
        last_record_function(needdata)
    
    if main_call_create_instance_model:
        print ('key_search_dict',key_search_dict)
        print ('update_dict',update_dict)
    obj_val, get_or_create  = get_or_create_instance(
                                                   self,
                                                   model_name,
                                                   key_search_dict,
                                                   update_dict,
                                                   not_create,
                                                   some_dict['instance_false'],
                                                   noti_dict,
                                                   inactive_include_search,
                                                   x2m_fields,
                                                   some_dict['remove_all_or_just_add_one_x2m'],
                                                   MODEL_DICT,
                                                   key_tram)
     
    
    return obj_val, get_or_create 
def check_notice_dict_co_create_or_get(model_name,noti_dict):
    print ('noti_dict***',noti_dict,'**model_name**',model_name)
    adict = noti_dict.get(model_name,{})
    if not adict.get('create') and not adict.get('update'):
        raise UserError(u'các row bị bỏ qua hết không có dòng nào được tạo hoặc được update')
    

def importthuvien(odoo_or_self_of_wizard,
                  model_dict = False,
                  key=False,
                  key_tram=False,
                  not_create = False):
    
    if not model_dict:
        ALL_MODELS_DICT = gen_model_dict()
    else:
        ALL_MODELS_DICT =  model_dict
    self = odoo_or_self_of_wizard
#     for r in self:
    if self.file ==False:
        raise UserError(u'Bạn phải upload file để import')
    file_content = base64.decodestring(self.file)
    if '.xlsx' in self.filename:
        formatting_info = False
    else:
        formatting_info = True
    xl_workbook = xlrd.open_workbook(file_contents = file_content, formatting_info=formatting_info)
    noti_dict = {}
    noti_dict['skip because required'] = 0
    if not key:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[self.type_choose]
    else:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[key]
    key_allow = CHOOSED_MODEL_DICT.get('key_allow',False)
    self_key_tram =  getattr(self,'key_tram',False) or key_tram
    key_tram = key_allow and self_key_tram
    if key_allow and not key_tram:
        raise UserError(u'ban phai chon key_tram')
    #recursive 1
    ordered_a_model_dict( CHOOSED_MODEL_DICT)
    
#     dac_tinhs = {}
#     xuat_het_dac_tinh(CHOOSED_MODEL_DICT,key_tram,dac_tinhs)
#     self.test_result_2 =u'kaka %s'% dac_tinhs 
#     return False
    #recursive 2
    recursive_add_model_name_to_field_attr(self,CHOOSED_MODEL_DICT,key_tram=key_tram)
#     ghom_dac_tinh = {}
#     rs = muon_xuat_dac_tinh_gi(CHOOSED_MODEL_DICT,ghom_dac_tinh=ghom_dac_tinh)
#     self.test_result_1 = rs
#     self.test_result_1 = ghom_dac_tinh
    sheet_names = get_key_allow(CHOOSED_MODEL_DICT, 'sheet_names', key_tram)
    if callable(sheet_names):
        try:
            sheet_names = sheet_names(self)
        except TypeError:
            sheet_names = sheet_names(self,xl_workbook)
    ######Khai bao needdata #####
    needdata = {}
    needdata['sheet_names'] = sheet_names
    #### end khai bao needdata#######
    needdata['key_tram'] = key_tram
    
    ### moi them
    not_create = get_key_allow(CHOOSED_MODEL_DICT, 'not_create', key_tram) or not_create
    if not_create:
        workbook_copy = copy(xl_workbook)
    else:
        workbook_copy = None
    ### end moi them  
    some_var_para = {}
#     break_condition_func_for_main_instance  = CHOOSED_MODEL_DICT.get('break_condition_func_for_main_instance')
    break_condition_func_for_main_instance  = get_key_allow(CHOOSED_MODEL_DICT,'break_condition_func_for_main_instance',key_tram)
    some_var_para['break_condition_func_for_main_instance'] = break_condition_func_for_main_instance
    
    for sheet_name in sheet_names:
        COPY_MODEL_DICT = deepcopy(CHOOSED_MODEL_DICT)
        needdata['sheet_name'] = sheet_name
        sheet = xl_workbook.sheet_by_name(sheet_name)
        # moi them:
        if not_create:
            sheet_of_copy_wb = workbook_copy.get_sheet(0)
        else:
            sheet_of_copy_wb = False
        title_rows = CHOOSED_MODEL_DICT.get('title_rows_some_sheets',{}).get(sheet_name)
        largest_map_row_choosing = get_key_allow(CHOOSED_MODEL_DICT, 'largest_map_row_choosing', key_tram)#largest_map_row_choosing  is boolean
        if largest_map_row_choosing:
            title_rows = range(0,sheet.nrows)
        else:
            title_rows = title_rows or get_key_allow(CHOOSED_MODEL_DICT, 'title_rows', key_tram)  # MODEL_DICT['title_rows']
        row_title_index,largest_map_row = define_col_index(title_rows,sheet,COPY_MODEL_DICT,key_tram)
        
        
#         type_cua_attr = {}
#         tim_type_cua_attr(COPY_MODEL_DICT,key_tram, type_cua_attr = type_cua_attr)
#         self.test_result_1 = type_cua_attr
#         
        
        if largest_map_row_choosing:
            row_title_index = largest_map_row
        print ('****row_title_index*******',row_title_index)
        merge_tuple_list =  sheet.merged_cells
        #recursive 3
        check_xem_att_co_nam_ngoai_khong(COPY_MODEL_DICT,key_tram)
        if row_title_index == None:
            raise UserError(u'row_title_index == None, không có xl_title nào match với excel')
        if not_create:
            write_get_or_create_title(CHOOSED_MODEL_DICT,sheet,sheet_of_copy_wb,row_title_index,key_tram)
        off_set_row = get_key_allow(CHOOSED_MODEL_DICT, 'begin_data_row_offset_with_title_row', key_tram, 1)
#         off_set_row = CHOOSED_MODEL_DICT.get('begin_data_row_offset_with_title_row',1)
        min_row = row_title_index + off_set_row
        first_row = min_row + getattr(self,'begin_row',0)
        print ('first_row','min_row',first_row,min_row)
        if not getattr(self,'dong_test',None):
            last_row = sheet.nrows
        else:
            last_row = first_row + self.dong_test
        if last_row >sheet.nrows:
            last_row =  sheet.nrows
        if first_row >  last_row :
            raise UserError(u'first_row >  last_row')
        
        #recursive 4
        check_col_index_match_xl_title(self,COPY_MODEL_DICT,key_tram,needdata)
       
        needdata['vof_dict'] = COPY_MODEL_DICT.get('fields') 
        for number_row_count,row in enumerate(range(first_row, last_row)):
            print ('sheet_name',sheet_name,'row',row)
            create_instance( self, COPY_MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,
                              main_call_create_instance_model=True,
                              key_tram=key_tram,
                              not_create = not_create,
                              workbook_copy = workbook_copy,
                              sheet_of_copy_wb = sheet_of_copy_wb,
                              some_var_para = some_var_para
                               )
        model_name = model_name = get_key_allow(COPY_MODEL_DICT, 'model', key_tram)
        check_notice_dict_co_create_or_get(model_name,noti_dict)
    if number_row_count:
        self.imported_number_of_row = number_row_count + 1
        
    
    last_import_function  = get_key_allow(CHOOSED_MODEL_DICT,'last_import_function',key_tram)
    if last_import_function:
        last_import_function(needdata,self)
    self.log= noti_dict
    return workbook_copy
    
            

            

