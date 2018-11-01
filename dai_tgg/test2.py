# -*- coding: utf-8 -*-s
from collections import OrderedDict
import re
 
# a = {
#     'replace_string': {
#         'types': ['list']
#     },
#     'raise_if_False': {
#         'types': ['bool']
#     },
#     'largest_map_row_choosing': {
#         'types': ['bool']
#     },
#     'not_create': {
#         'types': ['bool']
#     },
#     'last_record_function': {
#         'types': ['function']
#     },
#     'empty_val': {
#         'types': ['list']
#     },
#     'for_excel_readonly': {
#         'types': ['bool']
#     },
#     'string': {
#         'types': ['str']
#     },
#     'col_index': {
#         'types': ['int']
#     },
#     'skip_field_if_not_found_column_in_some_sheet': {
#         'types': ['bool', 'NoneType']
#     },
#     'key_ltk_dc': {
#         'types': ['list']
#     },
#     'offset_write_xl': {
#         'types': ['NoneType']
#     },
#     'set_val': {
#         'types': ['NoneType', 'str', 'function']
#     },
#     'func': {
#         'types': ['function', 'NoneType']
#     },
#     'required': {
#         'types': ['bool']
#     },
#     'xl_title': {
#         'types': ['str', 'list', 'NoneType']
#     },
#     'skip_this_field': {
#         'types': ['NoneType', 'bool']
#     },
#     'transfer_name': {
#         'types': ['NoneType']
#     },
#     'replace_val': {
#         'types': ['dict']
#     },
#     'bypass_this_field_if_value_equal_False': {
#         'types': ['bool']
#     },
#     'sheet_names': {
#         'types': ['function']
#     },
#     'last_import_function': {
#         'types': ['function']
#     },
#     'karg': {
#         'types': ['NoneType']
#     },
#     'begin_data_row_offset_with_title_row': {
#         'types': ['int']
#     },
#     'field_type': {
#         'types': ['str']
#     },
#     'title_rows': {
#         'types': ['list']
#     },
#     'get_or_create_para': {
#         'types': ['NoneType']
#     },
#     'key_tti_dc': {
#         'types': ['NoneType']
#     },
#     'model': {
#         'types': ['str']
#     },
#     'key': {
#         'types': ['bool']
#     },
#     'key_allow': {
#         'types': ['bool']
#     },
#     'title_rows_some_sheets': {
#         'types': ['dict']
#     },
#     'sheet_allow_this_field_not_has_exel_col': {
#         'types': ['list']
#     }
# }
# 
# 
# b =  OrderedDict(sorted(a.items()))
# for k,v in b.items():
#     print "'" + k + "'",':',v,','


# att_dict = {
# 'begin_data_row_offset_with_title_row' : {'types': ['int']} ,
# 'bypass_this_field_if_value_equal_False' : {'types': ['bool']} ,
# 'col_index' : {'types': ['int']} ,
# 'empty_val' : {'types': ['list']} ,
# 'field_type' : {'types': ['str']} ,
# 'for_excel_readonly' : {'types': ['bool']} ,
# 'func' : {'types': ['function', 'NoneType']} ,
# 'get_or_create_para' : {'types': ['NoneType']} ,
# 'karg' : {'types': ['NoneType']} ,
# 'key' : {'types': ['bool']} ,
# 'key_allow' : {'types': ['bool']} ,
# # 'key_ltk_dc' : {'types': ['list']} ,
# # 'key_tti_dc' : {'types': ['NoneType']} ,
# 'largest_map_row_choosing' : {'types': ['bool']} ,
# 'last_import_function' : {'types': ['function']} ,
# 'last_record_function' : {'types': ['function']} ,
# 'model' : {'types': ['str']} ,
# 'not_create' : {'types': ['bool']} ,
# 'offset_write_xl' : {'types': ['NoneType']} ,
# 'raise_if_False' : {'types': ['bool']} ,
# 'replace_string' : {'types': ['list']} ,
# 'replace_val' : {'types': ['dict']} ,
# 'required' : {'types': ['bool']} ,
# 'set_val' : {'types': ['NoneType', 'str', 'function']} ,
# 'sheet_allow_this_field_not_has_exel_col' : {'types': ['list']} ,
# 'sheet_names' : {'types': ['function']} ,
# 'skip_field_if_not_found_column_in_some_sheet' : {'types': ['bool', 'NoneType']} ,
# 'skip_this_field' : {'types': ['NoneType', 'bool']} ,
# 'string' : {'types': ['str']} ,
# 'title_rows' : {'types': ['list']} ,
# 'title_rows_some_sheets' : {'types': ['dict']} ,
# 'transfer_name' : {'types': ['NoneType']} ,
# 'xl_title' : {'types': ['str', 'list', 'NoneType']} ,
# }
# 
# def check_thuoc_tinh_co_nam(val,attr):
#     
#     if attr not in att_dict:
#         return False
#     else:
#         return True
# print check_thuoc_tinh_co_nam('ad',u'begin_data_row_offset_with_title_row')  

kq = re.search(u'Số thứ tự (trong shelf)', u'Số thứ tự (trong shelf)')
print (kq.group())