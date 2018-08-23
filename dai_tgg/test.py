# -*- coding: utf-8 -*-
from collections import defaultdict, Counter, OrderedDict
from copy import deepcopy


def lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE(MODEL_DICT, value_may_be_title, col,key_tram):
    #print 'value_may_be_title',value_may_be_title
    print ('in lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE...')
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
            is_real_xl_match_with_xl_excel = lOOP_THROUGH_FIELDS_IN_MODEL_DICT_TO_ADD_COL_INDEX_MATCH_XL_TITLE(field_attr, value_may_be_title, col)
        elif xl_title:
            if isinstance(xl_title, list):
                xl_title_s = xl_title
            else:
                xl_title_s = [xl_title]
            for xl_title in xl_title_s:
                if xl_title == value_may_be_title:
#                     if xl_title ==u'Ngăn' and value_may_be_title==u'Ngăn':
#                         raise UserError(u'kakaka Ngăn')
                    field_attr['col_index'] = col
                    is_real_xl_match_with_xl_excel = True        
        is_map_xl_title = is_map_xl_title or is_real_xl_match_with_xl_excel
    return is_map_xl_title #or is_map_xl_title_foreinkey