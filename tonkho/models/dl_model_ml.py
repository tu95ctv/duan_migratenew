# -*- coding: utf-8 -*-
#######################ML################################
import xlwt
from openerp.http import request
from odoo.addons.tonkho.models.dl_model import add_title
from collections import  OrderedDict
normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
horiz_center_normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align:  vert centre, horiz center; borders: left thin,right thin, top thin, bottom thin")
not_horiz_center_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align: wrap on , vert centre; borders: left thin,right thin, top thin, bottom thin")
header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ; align:  vert centre, horiz center ;  pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
def add_1_row_squant_new_ml(worksheet, move ,FIELDNAME_FIELDATTR, row_index, offset_column=0, f_name_slit_parrent = None, 
                            needdata=None,save_ndata=False,ml=False,
                            ml_index=False,rowspan=False):
    if save_ndata:
        a_instance_dict =  needdata.get('a_instance_dict', {})
    else:
        a_instance_dict = {}
    writen_column_number = 0
    col_index = 0
    col_index += offset_column
    
    for f_name,FIELDATTR in FIELDNAME_FIELDATTR.items():
#         f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        skip_field = FIELDATTR.get('skip_field')
        one_field_val = a_instance_dict.setdefault(f_name,{})
        if skip_field:
            continue
        if '.' in f_name:
            f_names = f_name.split('.')
            r = ml
#             is_ml_field = True
            if not is_not_model_field:
                f_name = f_names[-1]
                is_same = len(set(move.move_line_ids.mapped(f_name))) <=1
            else:
                is_same = FIELDATTR.get('is_same', False)
                
            print ('field','is_same',f_name,is_same)
        else:
            r = move
            is_same = FIELDATTR.get('is_same', True)
            if callable(is_same):
                is_same = is_same(move,ml)
        is_same = is_same if rowspan > 1 else False       
        split = FIELDATTR.get('split')
        fields = FIELDATTR.get('fields')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        
        
        if is_not_model_field:
            val = False
        else:
            val = getattr(r, f_name)
        
        one_field_val['val_before_func'] = val
        func = FIELDATTR.get('func',None)
        kargs = FIELDATTR.get('kargs',{})
        if func:
            val = func(val,needdata,move,ml, **kargs)

        if val == False:
            val = u''
            
        one_field_val['val']=val 
        if write_to_excel:
            if is_same:
                if ml_index==0:
                    worksheet.write_merge(row_index, row_index +rowspan-1, col_index,col_index,val,not_horiz_center_border_style)
            else:
                worksheet.write(row_index, col_index, val, not_horiz_center_border_style)
            writen_column_number +=1
            col_index +=1
        else:
            pass
#         if split:
#             a_instance_dict,writen_column_number_children = add_1_row_squant(worksheet,r ,split, row_index, offset_column=col_index  ,f_name_slit_parrent = f_name,needdata=needdata)
#             offset_column += writen_column_number_children -1 +  (1 if write_to_excel else 0)
#             writen_column_number += writen_column_number_children
#             one_field_val['split'] = a_instance_dict
#             col_index +=writen_column_number_children
#         if fields:
#             a_instance_dict,writen_column_number_children = add_1_row_squant(worksheet,ml ,fields, row_index, offset_column=col_index  ,f_name_slit_parrent = f_name,needdata=needdata)
#             offset_column += writen_column_number_children -1 +  (1 if write_to_excel else 0)
#             writen_column_number += writen_column_number_children
#             one_field_val['fields'] = a_instance_dict
#             col_index +=writen_column_number_children
    return a_instance_dict, writen_column_number


 
# normal_not_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ;align:  vert centre, horiz center;")


def download_model_new_ml(dlcv_obj, Export_Para=None,workbook=None,append_domain=None,sheet_name=None,worksheet=None,row_index=15):
    exported_model= Export_Para['exported_model']
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
    FIELDNAME_FIELDATTR = OrderedDict(FIELDNAME_FIELDATTR)
    gen_domain= Export_Para.get('gen_domain')
    if worksheet ==None:
        if workbook==None:
            workbook = xlwt.Workbook()
        sheet_name =  u'Sheet 1' if sheet_name ==None else sheet_name
        worksheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
    needdata = {'a_instance_dict':{'move_line_ids.stt_not_model':{'val':0}}}
    needdata['dlcv_obj'] = dlcv_obj
    if gen_domain:
        domain = gen_domain(dlcv_obj)
    else:
        domain = []
    if append_domain:
        domain.extend(append_domain)  
    order = Export_Para.get('search_para',{})
    all_objs = request.env[exported_model].search(domain,**order)
    model_fields = request.env[exported_model]._fields
    
    
#     skip_tinh_trang_field = set(dlcv_obj.move_line_ids.mapped('tinh_trang')) ==set(['tot']) and   dlcv_obj.is_ghom_tot
#     FIELDNAME_FIELDATTR['move_line_ids.tinh_trang']['skip_field'] = skip_tinh_trang_field
    
    add_title(worksheet, FIELDNAME_FIELDATTR, 
              model_fields, ROW_TITLE=row_index,
               offset_column=0,
               is_set_width = False,
#                is_auto_width = False
               )
    nrow = 0
    row_index +=1
    for move in all_objs:#request.env['cvi'].search([]):
        rowspan = len(move.move_line_ids)
        for ml_index, ml in enumerate(move.move_line_ids):
            nrow +=1
            add_1_row_squant_new_ml(worksheet, move , FIELDNAME_FIELDATTR, row_index, offset_column=0,needdata=needdata,save_ndata=True, ml=ml, ml_index=ml_index,rowspan=rowspan)
            row_index +=1
    return nrow



# def ghi_chu_(val,n,move,ml):
#     if not val:
#         return move.ghi_chu
#     else:
#         return val
def stt_ml_(v,needdata,m,ml): 
    v = needdata['a_instance_dict']['move_line_ids.stt_not_model']['val']  +1   
    return v    

def ghi_chu_(val,n,move,ml, all_tot = False, IS_SET_TT_COL=False):
    tinh_trang = ml.tinh_trang
    
    if not val:
        ghi_chu =  move.ghi_chu
    else:
        ghi_chu =  val
#     tt = n['a_instance_dict']['tinh_trang']['val']
    if not IS_SET_TT_COL and  not all_tot:
        if ghi_chu:
            ghi_chu =  u'%s, %s'%(tinh_trang,ghi_chu)
        else:
            ghi_chu = u'%s'%tinh_trang
    return ghi_chu
def is_same_(m,ml):
    if m.product_id.tracking == 'none':
        is_same = False
    else:
        is_same = True
    return is_same
def is_same_ghi_chu_(m,ml):
    is_same_tt = len(set(m.move_line_ids.mapped('tinh_trang'))) <=1
    is_same_gc = len(set(m.move_line_ids.mapped('ghi_chu'))) <=1
    is_same_gc = is_same_gc and is_same_tt
    return is_same_gc
def quantity_done_(v,n,m,l):
    if m.product_id.tracking == 'none':
        qty = l.qty_done
    else:
        qty = v
    return qty
TINH_TRANG = {'tot':u'Tốt','hong':u'Hỏng'}
def tinh_trang_(v,n,m,l):
    return TINH_TRANG[v]
    
# FIELDNAME_FIELDATTR_ML = [
#          ('move_line_ids.stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_ml_,'is_same':False }),
#          ('product_id',{'func':lambda v,n,m,ml: v.name,'width':get_width(50),'string':u'Tên vật tư' }),
#          ('move_line_ids.pn_id',{'func':lambda v,n,m,ml: v.name,'width':get_width(20),'string':u'Mã vật tư'}),
#          ('quantity_done',{'width':get_width(40),'is_same':is_same_,'func':quantity_done_,'string':u'Số lượng'}),
#          ('product_uom',{'func':lambda v,n,m,ml: v.name,'width':get_width(40),'string':u'ĐVT'}),
#          ('move_line_ids.lot_id',{'func':lambda v,n,m,ml: v.name,'width':get_width(20),'string':u'Serial Number'}),
#          ('move_line_ids.tinh_trang',{'string':u'Tình trạng','func':tinh_trang_,'skip_field':False}),
#          ('move_line_ids.ghi_chu',{'string':u'Ghi chú','func':ghi_chu_}),
#         ]


# def download_ml(dlcv_obj,workbook=None,append_domain=None,sheet_name=None,row_index=0):
#     return download_model_new_ml(dlcv_obj,Export_Para=Export_Para_ml,append_domain=append_domain,workbook=workbook,sheet_name=sheet_name,row_index=row_index)
def gen_domain_sml(dlcv_obj):
    domain = []
    domain.append(('picking_id','=',dlcv_obj.id))
    return domain
def download_ml_for_bb(dlcv_obj,workbook=None,append_domain=None,sheet_name=None,worksheet=None,row_index=0,
                       IS_SET_TT_COL=False,
                       all_tot=False):
#     all_tot = set(dlcv_obj.move_line_ids.mapped('tinh_trang')) ==set(['tot']) and   dlcv_obj.is_ghom_tot
    FIELDNAME_FIELDATTR_ML = [
         ('move_line_ids.stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_ml_,'is_same':False }),
         ('product_id',{'func':lambda v,n,m,ml: v.name,'string':u'Tên vật tư' }),
         ('move_line_ids.pn_id',{'func':lambda v,n,m,ml: v.name,'string':u'Mã vật tư'}),
         ('quantity_done',{'is_same':is_same_,'func':quantity_done_,'string':u'S/L'}),
         ('product_uom',{'func':lambda v,n,m,ml: v.name,'string':u'ĐVT'}),
         ('move_line_ids.lot_id',{'func':lambda v,n,m,ml: v.name,'string':u'Serial Number'}),
         ('move_line_ids.tinh_trang',{'string':u'T/T','func':tinh_trang_,'skip_field':not (IS_SET_TT_COL and not all_tot)}),
         ('move_line_ids.ghi_chu',{'string':u'Ghi chú','func':ghi_chu_,'is_same':is_same_ghi_chu_,'kargs':{'all_tot':all_tot, 'IS_SET_TT_COL':IS_SET_TT_COL}}),
        ]


    Export_Para_ml = {
        'exported_model':'stock.move',
        'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_ML,
        'gen_domain':gen_domain_sml,
        'search_para':{'order': 'stt asc'},#desc
        }
    
    return download_model_new_ml(dlcv_obj, Export_Para=Export_Para_ml, append_domain=append_domain,
                                 workbook=workbook,
                                 sheet_name=sheet_name,
                                 worksheet=worksheet,
                                 row_index=row_index) + 1