# TYPES_ATT_DICT = {
#             'begin_data_row_offset_with_title_row' : {'types': [int]} ,
#             'bypass_this_field_if_value_equal_False' : {'types': [bool]} ,
#             'col_index' : {'types': [int]} ,
#             'empty_val' : {'types': ['list']} ,
#             'field_type' : {'types': ['str']} ,
#             'for_excel_readonly' : {'types': [bool]} ,
#             'func' : {'types': ['function', 'NoneType']} ,
#             'get_or_create_para' : {'types': ['NoneType','dict'],'default':{}} ,#not_use_key: chưa xài
#             'karg' : {'types': ['NoneType']} ,#khong_can_khai_bao_key
#             'key' : {'types': [bool]} ,
#             'key_allow' : {'types': [bool]} ,
#             # 'key_ltk_dc' : {'types': ['list']} ,
#             # 'key_tti_dc' : {'types': ['NoneType']} ,
#             'largest_map_row_choosing' : {'types': [bool]} ,
#             'last_import_function' : {'types': ['function']} ,
#             'last_record_function' : {'types': ['function']} ,
#             'model' : {'types': ['str']} ,
#             'not_create' : {'types': [bool]} ,
#             'offset_write_xl' : {'types': ['NoneType',int]} ,
#             'raise_if_False' : {'types': [bool]} ,
#             'replace_string' : {'types': ['list']} ,
#             'replace_val' : {'types': ['dict']} ,
#             'required' : {'types': [bool]} ,
#             'set_val' : {'types': ['NoneType', 'str', 'function'],'no_need_check_type':True} ,
#             'sheet_allow_this_field_not_has_exel_col' : {'types': ['list']} ,
#             'sheet_names' : {'types': ['function','list']} ,
#             'skip_field_if_not_found_column_in_some_sheet' : {'types': [bool, 'NoneType']} ,
#             'skip_this_field' : {'types': ['NoneType', bool,'function']} ,
#             'string' : {'types': ['str']} ,
#             'title_rows' : {'types': ['list'],'no_need_check_type':True} ,
#             'title_rows_some_sheets' : {'types': ['dict']} ,
#             'transfer_name' : {'types': ['str']} ,
#             'xl_title' : {'types': ['str', 'list', 'NoneType']} ,
#             'inactive_include_search':{'types':[bool]},
#             'is_x2m_field':{'types':[bool]},
#             'remove_all_or_just_add_one_x2m':{'types':[bool]},
#             'break_condition_func_for_main_instance':{'types': [ 'function']} ,
#             'type_allow':{'types':['list']},
#             'for_create_another':{'types':[bool]},
#             'only_get':{'types':[bool]},
#             'required_not_create':{'types':[bool]},
#             'write_func':{'types': ['function']},
#             'mode_no_create_in_main_instance':{'types': [bool]},
#             'skip_this_field_for_mode_no_create':{'types': [bool]},
#             'required_force':{'types': [bool]},
#             'bypass_check_type':{'types':[bool]}
# #             'skip_field_default':{'types': [bool]}
# }
import re

pn = u'\ / -s'
pn_replace =  re.sub('[- _ \s \\\ \/]','',pn)
print ('ad',pn_replace)