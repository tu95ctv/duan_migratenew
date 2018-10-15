 # -*- coding: utf-8 -*-
from odoo.addons.dai_tgg.models.model_dict_folder.tool_tao_instance import get_key_allow
from odoo.osv import expression
import datetime
from odoo import  fields
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
            obj_id =  [(6,False,result)]
        else:
            obj_id =  [(4,result[0],False)]
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