# -*- coding: utf-8 -*-
from openerp.http import request
import datetime
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
from collections import  OrderedDict

def get_width(num_characters):
    return int((1+num_characters) * 256)

normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
horiz_center_normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align:  vert centre, horiz center; borders: left thin,right thin, top thin, bottom thin")
normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align:  vert centre ; borders: left thin,right thin, top thin, bottom thin")
not_horiz_center_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align: wrap on , vert centre; borders: left thin,right thin, top thin, bottom thin")
header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ; align:  vert centre, horiz center ;  pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
def download_model(dl_obj,
                    Export_Para=None,
                    workbook=None,
                    append_domain=None,
                    sheet_name=None):
#     global dl_obj_global
#     dl_obj_global = dl_obj
    exported_model= Export_Para['exported_model']
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
    FIELDNAME_FIELDATTR = recursive_OrderedDict(FIELDNAME_FIELDATTR)
#     print ('**FIELDNAME_FIELDATTR***',FIELDNAME_FIELDATTR)
    gen_domain= Export_Para.get('gen_domain')
    if workbook==None:
        workbook = xlwt.Workbook()
    if sheet_name ==None:
        sheet_name =  u'Sheet 1'
    worksheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
    needdata = {'a_instance_dict':{'stt_not_model':{'val':0}}}
    needdata['dl_obj'] = dl_obj
    model_fields = request.env[exported_model]._fields
    ROW_TITLE = 0
    OFFSET_COLUMN = 0
#     add_title(worksheet, FIELDNAME_FIELDATTR, model_fields, ROW_TITLE=ROW_TITLE, offset_column=OFFSET_COLUMN)
    if gen_domain:
        domain = gen_domain(dl_obj)
    else:
        domain = []
    if append_domain:
        domain.extend(append_domain)  
    order = Export_Para.get('search_para',{})
    squants = request.env[exported_model].search(domain,**order)
    row_index = ROW_TITLE + 1
    if not squants:
        return workbook
    for r in squants:#request.env['cvi'].search([]):
        add_1_row_squant(worksheet,r, FIELDNAME_FIELDATTR, row_index, offset_column=OFFSET_COLUMN,needdata=needdata,save_ndata=True)
        row_index +=1
    add_title(worksheet, FIELDNAME_FIELDATTR, model_fields, ROW_TITLE=ROW_TITLE, offset_column=OFFSET_COLUMN)
    return workbook


def add_1_row_squant(worksheet,r ,FIELDNAME_FIELDATTR, row_index, offset_column=0, f_name_slit_parrent = None,
                      needdata=None,save_ndata=False):
    if save_ndata:
        a_instance_dict =  needdata.get('a_instance_dict', {})
    else:
        a_instance_dict = {}
    writen_column_number = 0
    col_index = 0
    col_index += offset_column
    for  f_name,FIELDATTR in FIELDNAME_FIELDATTR.items():
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        split = FIELDATTR.get('split')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        if is_not_model_field:
            val = False
        else:
            val = getattr(r, f_name)
        one_field_val = a_instance_dict.setdefault(f_name,{})
        one_field_val['val_before_func'] = val
        func = FIELDATTR.get('func',None)
        kargs = FIELDATTR.get('kargs',{})
        if func:
            val = func(val,needdata, **kargs)
#         print (f_name, val)
        if val == False:
#             print ('FALSE',f_name,val)
            val = u''
        one_field_val['val']=val 
        max_len_field_val =  FIELDATTR.setdefault('max_len_field_val',0)
        val_len = len(val) if isinstance(val, str) else 0
        if val_len > max_len_field_val:
            FIELDATTR['max_len_field_val'] = val_len
        if  write_to_excel:
            worksheet.write(row_index, col_index, val, normal_border_style)
            writen_column_number +=1
            col_index +=1
        else:
            pass
        
        if split:
            a_instance_dict,writen_column_number_children = add_1_row_squant(worksheet,r ,split, row_index, offset_column=col_index  ,f_name_slit_parrent = f_name,needdata=needdata)
            offset_column += writen_column_number_children -1 +  (1 if write_to_excel else 0)
            writen_column_number += writen_column_number_children
            one_field_val['split'] = a_instance_dict
            col_index +=writen_column_number_children
    return a_instance_dict, writen_column_number
def add_title(worksheet,FIELDNAME_FIELDATTR,model_fields,ROW_TITLE=0, offset_column=0,
               is_set_width = True,
#               is_auto_width = True,
#                for_len_adj = False
               ):
    writen_column_number = 0
    column_index = offset_column
    for f_name, FIELDATTR in  FIELDNAME_FIELDATTR.items():
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        skip_field = FIELDATTR.get('skip_field')
        if skip_field:
            continue
        split = FIELDATTR.get('split')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        if is_not_model_field:
            f_string =FIELDATTR.get('string') or  f_name
        else:
            f_string =FIELDATTR.get('string')
            if not f_string:
                field = model_fields[f_name]
                f_string = field.string
        if write_to_excel:
            worksheet.write(ROW_TITLE, column_index, f_string, header_bold_style)
            writen_column_number += 1
            if is_set_width:
                
                width  = get_width(FIELDATTR.get('max_len_field_val') + 2) #or width
                f_string_width = get_width(len(f_string) + 2)
                if f_string_width > width:
                    width = f_string_width
                    
                    
                worksheet.col(column_index).width = width
            column_index +=1
        else:
            pass
        if split:
            writen_column_number_child = add_title(worksheet,split, model_fields,ROW_TITLE=ROW_TITLE, offset_column=column_index)
            print ("writen_column_number_child",writen_column_number_child)
            column_index +=writen_column_number_child
            writen_column_number += writen_column_number_child
    return writen_column_number
            






def recursive_OrderedDict (FIELDNAME_FIELDATTR):
    if isinstance(FIELDNAME_FIELDATTR,list):
        obj_loop= FIELDNAME_FIELDATTR
    else:
        obj_loop= FIELDNAME_FIELDATTR.items()
    for fname,attr in obj_loop:
        split = attr.get('split')
        if split:
            attr['split'] = recursive_OrderedDict(split)
    if isinstance(FIELDNAME_FIELDATTR,list):
        return OrderedDict(FIELDNAME_FIELDATTR)
    else:
        return FIELDNAME_FIELDATTR







