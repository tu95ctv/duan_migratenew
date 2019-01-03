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
from odoo.addons.dai_tgg.models.model_dict_folder.recursive_func import muon_xuat_dac_tinh_gi,ordered_a_model_dict,recursive_add_model_name_to_field_attr,define_col_index,define_col_index,check_xem_att_co_nam_ngoai_khong,write_get_or_create_title,check_col_index_match_xl_title,rut_gon_key
# from odoo.addons.dai_tgg.models.model_dict_folder.recursive_func import tim_type_cua_attr
MAP_TYPE = {
                      'integer':[int,float],
                      'float':float, 
                      'many2one':int,
                      'char':str,
                      'selection':str,
                      'text':str, 
                      'boolean':bool,
                      'many2many':list,
                      'one2many':list,
                      
                      
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
            pattern = pattern.replace('(','\(').replace(')','\)')
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
    if field_attr.get('bypass_check_type'):
        return True
    field_type = field_attr.get('field_type')
#     check_field_type = field_attr.get('check_field_type',True)
    if field_type:
        type_allow = field_attr.get('type_allow',[])
        if val != False and val != None:
            try:
                class_or_type_or_tuple = MAP_TYPE[field_type]
            except:
                return True
                raise UserError(u'không có field_type:%s này'%field_type)
            if field_attr.get('is_x2m_field'):
                class_or_type_or_tuple = list
            if isinstance( class_or_type_or_tuple,list):
                type_allow.extend(class_or_type_or_tuple)
            else:
                type_allow.append(class_or_type_or_tuple)
            pass_type_check = False
            for a_type_allow in type_allow:
                if isinstance(val, a_type_allow):
                    pass_type_check = True
                    continue
            if not pass_type_check:
                raise UserError(u'model: %s- field:%s có giá trị: %s, đáng lẽ là field_type:%s nhưng lại có type %s'%(model_name, field_name,val,field_type,type(val)))
#     else:
#         raise UserError(u'Không có field_type:%s trong biến MAP_TYPE'%(field_type))      
def read_val_for_ci(self,set_val,col_index,
                    a_field_vof_dict,
                    MODEL_DICT,
                    field_attr,
                    sheet,row,
                    merge_tuple_list,
                    not_create,
                    needdata,
                    noti_dict,
                    key_tram,
#                     workbook_copy,
                    sheet_of_copy_wb,
                    setting,
                    some_dict
                    ):  
    
    ### end  deal skip_field_cause_first_import####
    val = False
    obj = False
#     field_type_of_this_model = MODEL_DICT.get('field_type')
#     if callable(set_val):
#         set_val = set_val(self)

#     set_val_instead_loop_fields = field_attr.get('set_val_instead_loop_fields')
#     if callable(set_val_instead_loop_fields):
#         set_val_instead_loop_fields = set_val_instead_loop_fields(needdata,self)
#     if set_val_instead_loop_fields and  not not_create:
#         val = set_val_instead_loop_fields
    if set_val != None:
        val = set_val
        if MODEL_DICT.get('print_write_dict_new',False):
            print ('***set_val',set_val)
    elif col_index !=None: # đọc file exc
        xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
        a_field_vof_dict['excel_val'] = xl_val
        val = empty_string_to_False(xl_val)
#         if val != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('is_x2m_field'):
        if val != False and field_attr.get('is_x2m_field'):
            val = val.split(',')
            val = list(map(lambda i: empty_string_to_False(i.strip()),val))
            for i in val:
                if i==False:
                    raise UserError(u'Không được = False')
                
            
    
    elif field_attr.get('fields') :
        exist_val_before_loop_fields_func = setting.get('cho_phep_exist_val_before_loop_fields_func') and field_attr.get('exist_val_before_loop_fields_func')
        check_excel_obj_is_exist_func = field_attr.get('check_excel_obj_is_exist_func') 
        check_excel_obj_is_exist_func =   setting.get('allow_check_excel_obj_is_exist_func') and check_excel_obj_is_exist_func
        
#         exist_val_before_loop_fields_func2 =  field_attr.get('exist_val_before_loop_fields_func2')
        
#         if exist_val_before_loop_fields_func2:
#             exist_val = exist_val_before_loop_fields_func2(needdata,self) #1,True ; F,False
#         else:write_when_val_exist
#             exist_val = False
#             
      
        if exist_val_before_loop_fields_func:
            exist_val = exist_val_before_loop_fields_func(needdata,self) #1,True ; F,False
        else:
            exist_val = False
    
        if exist_val:
            write_when_val_exist = setting['write_when_val_exist']
            if write_when_val_exist:
                not_create2 = False
#                 exist_val = exist_val
            else:
                if check_excel_obj_is_exist_func:
                    not_create2 = True
#                     exist_val = False
        else:
            not_create2 = False
#             exist_val = False
#         some_dict['exist_val'] = exist_val
#         model = field_attr.get('model')
        if not exist_val or (exist_val and (check_excel_obj_is_exist_func or write_when_val_exist)) or not_create:
            search_func_para = {'exist_val':exist_val}
            obj,val, get_or_create  = create_instance (self, field_attr,sheet, 
                                                                    row, 
                                                                    merge_tuple_list,
                                                                    needdata, 
                                                                    noti_dict,
                                                                    key_tram=key_tram, 
                                                                    not_create = not_create ,
                                                                    sheet_of_copy_wb = sheet_of_copy_wb,
                                                                    not_create2 = not_create2,  #not_create2 : just get get_or_create
                                                                    exist_val = exist_val,
                                                                    search_func_para=search_func_para,
                                                                    setting=setting,
                                                                    
                                                                   )

        if exist_val:
            if  check_excel_obj_is_exist_func:# and not get_or_create:,not write_when_val_exist and
                try:
                    check_excel_obj_is_exist_func(get_or_create, obj, exist_val)
                except UserError as e:
                    if setting ['allow_check_excel_obj_is_exist_raise_or_break'] =='break':
                        return False,False,'break'
                    else:
                        raise UserError(e.args)
                        
#                         print ('ahahaha')
#                         raise UserError(e.args)
            val= exist_val.id
            obj = exist_val
            get_or_create = True
            this_model_notice = noti_dict.setdefault(field_attr.get('model'),{})
            this_model_notice['exist_val'] = this_model_notice.get('exist_val',0) + 1
        a_field_vof_dict['get_or_create'] = get_or_create
        if not_create:
            offset_write_xl = get_key_allow(field_attr, 'offset_write_xl', key_tram,None)
            if offset_write_xl !=None:
                if get_or_create:
                    get_or_create_display = u'Đã Có' 
                else:
                    if field_attr['fields']['name']['val'] !=False:
                        get_or_create_display = u'Chưa'
                    else:
                        get_or_create_display = u'empty cell'
                sheet_of_copy_wb.write(row,sheet.ncols + offset_write_xl , get_or_create_display,not_horiz_center_border_style)
    return obj,val,True      
#F1 
def get_a_field_val(self,field_name,field_attr,key_tram,
                            needdata,row,sheet,
                            MODEL_DICT,
                           not_create,
#                            workbook_copy,
                           sheet_of_copy_wb,
                           merge_tuple_list,model_name,main_call_create_instance_model,noti_dict,
                           key_search_dict,update_dict,x2m_fields,
                           some_dict,
                           setting
                           ):
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
    #F11
    obj,val,code = read_val_for_ci(self,set_val,col_index,
                    a_field_vof_dict,
                    MODEL_DICT,
                    field_attr,sheet,row,
                    merge_tuple_list
                    ,not_create,
                    needdata,noti_dict,key_tram,
#                     workbook_copy,
                    sheet_of_copy_wb,
                    setting,
                    some_dict
                    )
    if code =='break':
        return 'break_because_required'
    a_field_vof_dict['before_func_val'] = val
    # func
    karg = get_key_allow( field_attr,'karg',key_tram,{})
    if karg ==None:
        karg ={}
    if func:
        try:
            val = func(val, needdata,**karg)
        except TypeError:
            try:
                val = func(val, needdata,self,**karg)
            except TypeError:
                val = func(val,**karg)
    #end func
    val =replace_val_for_ci(field_attr,key_tram,val,needdata)
    a_field_vof_dict['val'] = val
    a_field_vof_dict['obj'] = obj
    
    
    
    
  
        
    
    if not_create:     
        required_when_normal  = get_key_allow(field_attr, 'required',key_tram, False)   
        required   = get_key_allow(field_attr, 'required_not_create',key_tram, required_when_normal) 
#         required_when_normal = False if bypass_this_field_if_value_equal_False else required_when_normal
        
        if (required_when_normal and val==False) and required ==False:
            some_dict['instance_false'] = True
    else:
        required = get_key_allow(field_attr, 'required',key_tram, False)  
#         required = False if bypass_this_field_if_value_equal_False else required

#         required = required and not bypass_this_field_if_value_equal_False
            
    #### !!! deal required #####    
    
    
   
    key_or_not = field_attr.get('key')
    if callable(key_or_not):
        key_or_not = key_or_not(needdata)
    bypass_this_field_if_value_equal_False = get_key_allow(field_attr, 'bypass_this_field_if_value_equal_False', key_tram, None)
    if bypass_this_field_if_value_equal_False ==None:
        bypass_this_field_if_value_equal_False = setting['bypass_this_field_if_value_equal_False_default']
#     if key_or_not ==True or key_or_not =='Both':
#         bypass_this_field_if_value_equal_False = False
#     print ('**val !=0.0',val !=0.0,val)
#     print (val, type(val))
    if required and (val==False and isinstance(val, bool)):# val ==False <==> val ==0, val ==0 <==> val =False
        if field_attr.get('raise_if_False'):
            raise UserError('raise_if_False field: %s'%field_name)
        if main_call_create_instance_model or MODEL_DICT.get('print_write_dict_new',False):
            print (u'skip việc get or create của dòng này because required but,model %s- field %s, val:%s'%(model_name,field_name,val))
        this_model_notice = noti_dict.setdefault(model_name,{})
        skip_because_required = this_model_notice.setdefault('skip_because_required',0)
        this_model_notice['skip_because_required'] = skip_because_required + 1
        return 'break_because_required' #sua 5
    elif bypass_this_field_if_value_equal_False and val==False:
        return 'continue'
    elif not field_attr.get('for_excel_readonly'):
        
        if key_or_not==True:
            key_search_dict [field_name] = val
        elif key_or_not == 'Both':
            key_search_dict [field_name] = val
            update_dict [field_name] = val
        else:
            update_dict [field_name] = val
#         print ('4',count)


    valid_field_func = field_attr.get('valid_field_func')
    if valid_field_func:
        valid_field_func(val,obj,needdata,self)
        
        
    print ("row: ", row,'model_name: ',model_name,'-field: ', field_name, '-val: ', val)
    check_type_of_val(field_attr,val,field_name,model_name)
    
    if field_attr.get('is_x2m_field'):
            x2m_fields.append(field_name)
            some_dict['remove_all_or_just_add_one_x2m'] &= field_attr.get('remove_all_or_just_add_one_x2m',True)
#     return instance_false
    return False        
#F2
def get_or_create_instance(self,
                           model_name,
                           key_search_dict,
                           update_dict,
                           not_create,
#                            instance_false,
                           noti_dict,
                           inactive_include_search,
                           x2m_fields,
                           remove_all_or_just_add_one_x2m,
                           MODEL_DICT,key_tram,
                           mode_no_create_in_main_instance,
                           not_create2=False,
                           exist_val = False,
                           search_func_para={},
                           setting={},
                           some_dict={}
                           ):
    if key_search_dict or MODEL_DICT.get('search_func'):
        if mode_no_create_in_main_instance:
            return False,False, False
        if model_name =='product.product':
            print ('key_search_dict',key_search_dict)
            
        
        obj,obj_val, get_or_create = get_or_create_object_has_x2m(self, model_name,
                                                                   key_search_dict, 
                                                                   update_dict,
#                                 is_must_update = True, 
                                noti_dict = noti_dict,
                                inactive_include_search  = inactive_include_search, 
                                x2m_field = x2m_fields[0] if x2m_fields else False,
                                remove_all_or_just_add_one_x2m=remove_all_or_just_add_one_x2m,
#                                 is_return_get_or_create = True,
                                model_dict=MODEL_DICT,
                                key_tram = key_tram,
                                not_create = not_create or not_create2,
                                exist_val=exist_val,
                                search_func_para=search_func_para,
                                setting=setting,
                                some_dict=some_dict
                                )
        return obj,obj_val, get_or_create 
    else:
        raise UserError(u'Không có Key search dict, model_name%s'%model_name)
#         return False,False,False  

################# CREATE INSTANCE
def create_instance (self, MODEL_DICT,
                    sheet, row,
                     merge_tuple_list,
                     needdata, noti_dict, 
                     main_call_create_instance_model = False,
                    key_tram=None, 
                    not_create = False,
                    sheet_of_copy_wb = False,
                    mode_no_create_in_main_instance = False,
                    not_create2 = False,
                    setting={},
                    exist_val = False,
                    search_func_para={},
                     ):
    key_search_dict = {}
    update_dict = {}
    model_name = get_key_allow(MODEL_DICT, 'model', key_tram)
    x2m_fields = []
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    some_dict = {'remove_all_or_just_add_one_x2m':True}#'instance_false':False,'
    break_condition = False
    for field_name,field_attr  in MODEL_DICT['fields'].items():
        code = get_a_field_val(self,field_name,field_attr,key_tram,needdata,row,sheet,
                            MODEL_DICT,
                           not_create,
                           sheet_of_copy_wb,
                           merge_tuple_list,model_name,main_call_create_instance_model,noti_dict,
                           key_search_dict,update_dict,x2m_fields,
                           some_dict,setting)
        if code =='break_because_required':
            break_condition = True# moi them
            break
    if break_condition:
        if main_call_create_instance_model:
            if  True:#getattr(self, 'allow_cate_for_ghi_chu',False):
                break_condition_func_for_main_instance  = get_key_allow(MODEL_DICT,'break_condition_func_for_main_instance',key_tram)
                if break_condition_func_for_main_instance:
                    break_condition_func_for_main_instance(needdata)
        obj_val = False
        get_or_create = False
        return False, obj_val,get_or_create
    if some_dict.get('instance_false'):
        return None,None,False
    
    last_record_function = get_key_allow(MODEL_DICT, 'last_record_function', key_tram)
    if last_record_function:
        last_record_function(needdata,self)
    
    if main_call_create_instance_model:
        pass
        print ('key_search_dict',key_search_dict)
        print ('update_dict',update_dict)
    obj,obj_val, get_or_create  = get_or_create_instance(
                                                   self,
                                                   model_name,
                                                   key_search_dict,
                                                   update_dict,
                                                   not_create,
#                                                    some_dict['instance_false'],
                                                   noti_dict,
                                                   inactive_include_search,
                                                   x2m_fields,
                                                   some_dict['remove_all_or_just_add_one_x2m'],
                                                   MODEL_DICT,
                                                   key_tram,
                                                   mode_no_create_in_main_instance,
                                                   not_create2=not_create2,
                                                   exist_val=exist_val,
                                                   search_func_para=search_func_para,
                                                   
                                                   
                                                   setting=setting,
                                                   some_dict=some_dict)
    return obj,obj_val, get_or_create 
def check_notice_dict_co_create_or_get(model_name,noti_dict,not_create,mode_no_create_in_main_instance):
    adict = noti_dict.get(model_name,{})
    if not adict.get('create') and not adict.get('update') and not not_create and not mode_no_create_in_main_instance:
        raise UserError(u'các row bị bỏ qua hết không có dòng nào được tạo hoặc được update')
    

def importthuvien(odoo_or_self_of_wizard,
                  model_dict = False,
                  key=False,
                  key_tram=False,
                  not_create = False):
    self = odoo_or_self_of_wizard
    
    
    
    self_key_tram =  getattr(self,'key_tram',False) or key_tram

    
    if not model_dict:
        ALL_MODELS_DICT = gen_model_dict(self=self, 
                                         key_tram = self_key_tram)
    else:
        ALL_MODELS_DICT =  model_dict
    
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
#     noti_dict['skip because required'] = 0
    if not key:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[self.type_choose]
    else:
        CHOOSED_MODEL_DICT = ALL_MODELS_DICT[key]
    context = {'from_import':True} 
    context_get = CHOOSED_MODEL_DICT.get('context')
    if context_get:
        context.update(context_get)
    self = self.with_context(context)
   
    
    key_allow = CHOOSED_MODEL_DICT.get('key_allow',False)
    key_tram = key_allow and self_key_tram
    if key_allow and not key_tram:
        raise UserError(u'ban phai chon key_tram')
    #R2
    mode_no_create_in_main_instance = getattr(self,'mode_no_create_in_main_instance',None)
    rut_gon_key(CHOOSED_MODEL_DICT,key_tram,mode_no_create_in_main_instance=mode_no_create_in_main_instance)
    print ('***CHOOSED_MODEL_DICT***',CHOOSED_MODEL_DICT)
    
    #R1
    ordered_a_model_dict( CHOOSED_MODEL_DICT)
    
    #R3
    recursive_add_model_name_to_field_attr(self,CHOOSED_MODEL_DICT,key_tram=key_tram)
#     dac_tinhs = {}
#     xuat_het_dac_tinh(CHOOSED_MODEL_DICT,key_tram,dac_tinhs)
#     self.test_result_2 =u'kaka %s'% dac_tinhs 
#     return False

#     ghom_dac_tinh = {}
#     rs = muon_xuat_dac_tinh_gi(CHOOSED_MODEL_DICT,attr_muon_xuats = ['skip_this_field'],ghom_dac_tinh=ghom_dac_tinh)
#     self.test_result_1 = rs
#     return False
#     self.test_result_1 = ghom_dac_tinh

    #R3 check_xem_att_co_nam_ngoai_khong
#     check_xem_att_co_nam_ngoai_khong(CHOOSED_MODEL_DICT,key_tram)

    
    sheet_names = get_key_allow(CHOOSED_MODEL_DICT, 'sheet_names', key_tram)
    if callable(sheet_names):
        try:
            sheet_names = sheet_names(self)
        except TypeError:
            sheet_names = sheet_names(self,xl_workbook)
    needdata = {}
    needdata['sheet_names'] = sheet_names
    needdata['key_tram'] = key_tram
    

#     some_var_para = {}
#     break_condition_func_for_main_instance  = get_key_allow(CHOOSED_MODEL_DICT,'break_condition_func_for_main_instance',key_tram)
#     some_var_para['break_condition_func_for_main_instance'] = break_condition_func_for_main_instance
    
    setting = CHOOSED_MODEL_DICT.get('setting',{})
    
        
    if hasattr(self, 'not_update_field_if_instance_exist_default'):
        not_update_field_if_instance_exist_default =  self.not_update_field_if_instance_exist_default
    else:
        not_update_field_if_instance_exist_default = CHOOSED_MODEL_DICT.get('not_update_field_if_instance_exist_default',False)
    
    
    setting['not_update_field_if_instance_exist_default'] = not_update_field_if_instance_exist_default
    
    if hasattr(self, 'bypass_this_field_if_value_equal_False_default'):
        bypass_this_field_if_value_equal_False_default =  self.bypass_this_field_if_value_equal_False_default
    else:
        bypass_this_field_if_value_equal_False_default = CHOOSED_MODEL_DICT.get('bypass_this_field_if_value_equal_False_default',False)
    setting['bypass_this_field_if_value_equal_False_default'] = bypass_this_field_if_value_equal_False_default
    
    setting2 = CHOOSED_MODEL_DICT.get('setting2',{})
    if setting2:
        setting.update(setting2)
#     if hasattr(self, 'write_when_val_exist'):
#         write_when_val_exist =  self.write_when_val_exist
#     else:
#         write_when_val_exist = CHOOSED_MODEL_DICT.get('write_when_val_exist',True)
#     setting['write_when_val_exist'] = write_when_val_exist
#     
#     
#     if hasattr(self, 'allow_check_excel_obj_is_exist_func'):
#         allow_check_excel_obj_is_exist_func =  self.allow_check_excel_obj_is_exist_func
#     else:
#         allow_check_excel_obj_is_exist_func = CHOOSED_MODEL_DICT.get('allow_check_excel_obj_is_exist_func',True)
#     
#     setting['allow_check_excel_obj_is_exist_func'] = allow_check_excel_obj_is_exist_func
    
    
    
    
    
#     print ('**setting**',setting)
#     raise UserError(u'%s'%setting)
    prepare_func = CHOOSED_MODEL_DICT.get('prepare_func')
    if prepare_func:
        prepare_func(needdata,self)
    for sheet_name in sheet_names:
        print ('**sheet_name',sheet_name)
        COPY_MODEL_DICT = deepcopy(CHOOSED_MODEL_DICT)
        needdata['vof_dict'] = COPY_MODEL_DICT.get('fields') 
        needdata['sheet_name'] = sheet_name
#         if key_tram:
#             rut_gon_key(COPY_MODEL_DICT,key_tram)
        sheet = xl_workbook.sheet_by_name(sheet_name)
        #R3 xuat dac tinh
        if getattr(self,'dac_tinh',None):
            dt = self.dac_tinh.split(',')
            
            dactinh = muon_xuat_dac_tinh_gi(COPY_MODEL_DICT, attr_muon_xuats = dt,ghom_dac_tinh = {})
            print ('***dactinh',dactinh)
            self.test_result_1 =  dactinh
            self.test_result_2 =  COPY_MODEL_DICT
            if self.only_xuat_thuoc_tinh:
                if not dt:
                    raise UserError(u'bạn phải chọn thuộc tính gì đó')
                return False
        
        #R4 define_col_index
        
        largest_map_row_choosing = get_key_allow(CHOOSED_MODEL_DICT, 'largest_map_row_choosing', key_tram)#largest_map_row_choosing  is boolean
      
        if largest_map_row_choosing:
            range_1 = getattr(self, 'range_1',None)
            range_2 = getattr(self, 'range_2',None)
            range_1 = range_1 or 0
            range_2 = range_2 or sheet.nrows
            title_rows = range(range_1,range_2)
        else:
            title_rows_some_sheets = CHOOSED_MODEL_DICT.get('title_rows_some_sheets',{})
            if title_rows_some_sheets:
                title_rows_some_sheets=title_rows_some_sheets.get(sheet_name)
            if title_rows_some_sheets:
                title_rows = title_rows_some_sheets
            else:
                title_rows = get_key_allow(CHOOSED_MODEL_DICT, 'title_rows', key_tram)  # MODEL_DICT['title_rows']
        
        
        row_title_index,largest_map_row = define_col_index(title_rows,sheet,COPY_MODEL_DICT,key_tram)
        if largest_map_row_choosing:
            row_title_index = largest_map_row
            
#         if largest_map_row_choosing:
#             row_title_index = largest_map_row
#         else:
        if row_title_index == None:
            raise UserError(u'row_title_index == None, không có xl_title nào match với excel')
        
        #!R4
        
        check_col_index_match_xl_title(self,COPY_MODEL_DICT,key_tram,needdata)
      
        
        off_set_row = get_key_allow(CHOOSED_MODEL_DICT, 'begin_data_row_offset_with_title_row', key_tram, 1)
        min_row = row_title_index + off_set_row
        first_row = min_row + getattr(self,'begin_row',0)
        print ('first_row','min_row',first_row,min_row)
       
        dong_test = getattr(self,'dong_test',None) or CHOOSED_MODEL_DICT.get('dong_test')
        if not dong_test:
            last_row = sheet.nrows
        else:
            last_row = first_row + dong_test
       
        if last_row > sheet.nrows:
            last_row =  sheet.nrows
        if first_row >  last_row :
            raise UserError(u'first_row >  last_row')
        
#         print ('***COPY_MODEL_DICT',COPY_MODEL_DICT)
        
       
        
        
        
#         not_create = get_key_allow(CHOOSED_MODEL_DICT, 'not_create', key_tram) or not_create
        if not_create:
            workbook_copy = copy(xl_workbook)
            sheet_of_copy_wb = workbook_copy.get_sheet(0)
            write_get_or_create_title(CHOOSED_MODEL_DICT,sheet,sheet_of_copy_wb, row_title_index, key_tram)
        else:
            workbook_copy = None
            sheet_of_copy_wb = None
        #!R7
        
        
        merge_tuple_list =  sheet.merged_cells
        
        for number_row_count,row in enumerate(range(first_row, last_row)):
            print ('sheet_name*******',sheet_name,'row',row)
#             COPY_MODEL_DICT_old = deepcopy(COPY_MODEL_DICT)
            create_instance (self, COPY_MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,
                              main_call_create_instance_model=True,
                              key_tram=key_tram,
                              not_create = not_create,
                              sheet_of_copy_wb = sheet_of_copy_wb,
                              mode_no_create_in_main_instance = mode_no_create_in_main_instance,
                              setting=setting
                               )
        model_name = get_key_allow(COPY_MODEL_DICT, 'model', key_tram)
        
#         check_notice_dict_co_create_or_get(model_name,noti_dict,not_create,mode_no_create_in_main_instance)
    if number_row_count:
        self.imported_number_of_row = number_row_count + 1
        
    
    last_import_function  = get_key_allow(CHOOSED_MODEL_DICT,'last_import_function',key_tram)
    if last_import_function:
        last_import_function(needdata,self)
    self.log= noti_dict
    return workbook_copy
    
            

            

