# -*- coding: utf-8 -*-
from collections import defaultdict, Counter, OrderedDict
from copy import deepcopy

# model_dict =  {
#                 'title_rows' : [1], 
#                 'begin_data_row_offset_with_title_row' :1,
#                 'sheet_names': [u'Location'],
#                 'model':'stock.location',
#                 'fields' : [
#                          ('name',{'func':None,'xl_title':u'Tên','key':True,'required':True}),
#                         ('location_id',{
#                             'fields':[
#                                                 ('name',{'set_val':u'Kho Đài HCM','key':True,'required':True}),
#                                                        ]
#                                             }
#                          ),
#                               ('location_id2',{
#                             'fields':[
#                                                 ('name2',{
#                                                     'fields':[
#                                                 ('name',{'set_val':u'Kho Đài HCM','key':True,'required':True}),
#                                                        ]
#                                                     
#                                                     }),
#                                                        ]
#                                             }
#                          ),
#                       ]
#                 }

# def f_ordered_a_model_dict(model_dict):
#     fields = model_dict['fields']
#     for fname,attr in fields:
#         childrend_model_dict=  attr
#         childrend_fields = childrend_model_dict.get('fields')
#         if childrend_fields:
#             new_ordered_dict = f_ordered_a_model_dict(childrend_model_dict)
#     model_dict['fields']=OrderedDict(fields)
#             
# f_ordered_a_model_dict(model_dict)
# print model_dict.items()
            
adict = OrderedDict()
adict['a']={'val':5,'key':True}
adict['b']={'val':2,'key':False}

print filter(lambda i:i,adict)