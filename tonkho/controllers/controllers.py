# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
import datetime
from odoo.tools.misc import xlwt
from odoo.addons.dai_tgg.mytools import  convert_date_odoo_to_str_vn_date
from odoo.exceptions import UserError



# dlcv_obj_global = None
def get_width(num_characters):
    return int((1+num_characters) * 256)
normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align:  vert centre, horiz center; borders: left thin,right thin, top thin, bottom thin")
# needdata ={}

header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ;  pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
def add_title(worksheet,FIELDNAME_FIELDATTR,model_fields,ROW_TITLE=0, offset_column=0, is_set_width = True):
    writen_column_number = 0
    column_index = 0
    column_index+= offset_column
    for c, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
#         col_index += offset_column
        f_name, FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
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
                width  = FIELDATTR.get('width')
                if not width :
                    width = get_width(len(f_string))
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
            
def add_1_row_squant(worksheet,r ,FIELDNAME_FIELDATTR, row_index, offset_column=0, f_name_slit_parrent = None, needdata=None,save_ndata=False):
    if save_ndata:
        a_instance_dict =  needdata.get('a_instance_dict', {})
    else:
        a_instance_dict = {}
    writen_column_number = 0
    col_index = 0
    col_index += offset_column
    for c, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
        f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        split = FIELDATTR.get('split')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
#         if f_name_slit_parrent:
#             val = getattr(r, f_name_slit_parrent)
#         else:
        if is_not_model_field:
            val = False
        else:
            val = getattr(r, f_name)
        one_field_val = a_instance_dict.setdefault(f_name,{})
        one_field_val['val_before_func'] = val
        func = FIELDATTR.get('func',None)
        karg = FIELDATTR.get('karg',{})
        
        if func:
            val = func(val,needdata, **karg)
        print (f_name, val)
        if val == False:
            print ('FALSE',f_name,val)
            val = u''
            
        
        one_field_val['val']=val 
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








def download_model(dlcv_obj, Export_Para=None,workbook=None,append_domain=None,sheet_name=None):
#     global dlcv_obj_global
#     dlcv_obj_global = dlcv_obj
    
    exported_model= Export_Para['exported_model']
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
    gen_domain= Export_Para.get('gen_domain')
    if workbook==None:
        workbook = xlwt.Workbook()
    if sheet_name ==None:
        sheet_name =  u'Sheet 1'
    worksheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
    needdata = {'a_instance_dict':{'stt_not_model':{'val':0}}}
    needdata['dlcv_obj'] = dlcv_obj
    model_fields = request.env[exported_model]._fields
    ROW_TITLE = 0
    OFFSET_COLUMN = 0
    add_title(worksheet, FIELDNAME_FIELDATTR, model_fields, ROW_TITLE=ROW_TITLE, offset_column=OFFSET_COLUMN)
    if gen_domain:
        domain = gen_domain(dlcv_obj)
    else:
        domain = []
    if append_domain:
        domain.extend(append_domain)  
    order = Export_Para.get('search_para',{})
    squants = request.env[exported_model].search(domain,**order)
    row_index = ROW_TITLE + 1
    for r in squants:#request.env['cvi'].search([]):
        add_1_row_squant(worksheet,r, FIELDNAME_FIELDATTR, row_index, offset_column=OFFSET_COLUMN,needdata=needdata,save_ndata=True)
        row_index +=1
    return workbook




def stt_(v,needdata): 
    v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
    return v      

def stt_ml_(v,needdata,m,ml): 
    v = needdata['a_instance_dict']['move_line_ids.stt_not_model']['val']  +1   
    return v      


def pr_running_quant_(v,n,parent_location_id='parent_location_id'):
        domain_quant = [('product_id','=',n['a_instance_dict']['id']['val']),('location_id','child_of',getattr(n['dlcv_obj'], parent_location_id).id)]#dlcv_obj_global
        Quant = request.env['stock.quant']
        try:
            item = Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id')[0]
            quant = item['quantity']
        except IndexError:
            quant = 0
        return quant
FIELDNAME_FIELDATTR_PRODUCT = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
         ('id',{}),
         ('name',{}),
         ('categ_id',{'func':lambda v,n: v.name}),
         ('pr_running_quant',{'is_not_model_field':True,'func':pr_running_quant_,'karg':{'parent_location_id':'parent_location_runing_id'}}),
         ('pr_prepare_quant',{'is_not_model_field':True,'func':pr_running_quant_}),
                    ]
Export_Para_product = {
'exported_model':'product.product',
'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_PRODUCT,
'gen_domain':None,
'search_para':{'order': 'id asc'},#desc
}
    
    
def download_product(dlcv_obj):
    return download_model(dlcv_obj,Export_Para=Export_Para_product)
def download_quants_moi_cage_moi_sheet(dlcv_obj):
    Quant = request.env['stock.quant']#.search([])
    cates = Quant.search([]).mapped('categ_id')
    workbook = xlwt.Workbook()
    for cate in cates:
        download_quants(dlcv_obj,workbook=workbook,append_domain=[('categ_id','=',cate.id)],sheet_name=cate.name)
    return workbook


def tu_shelf_(v,needdata, stock_type=None):
    location_id = needdata['a_instance_dict']['location_id']['val_before_func']
    l_id = request.env['stock.location'].search([('id','parent_of',location_id.id),('stock_type','=',stock_type)])
    return l_id.name

def gen_domain_stock_quant(dlcv_obj):
    domain = []
    if dlcv_obj.parent_location_id:
        domain.append(('location_id','child_of',dlcv_obj.parent_location_id.id))
    return domain
FIELDNAME_FIELDATTR = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
         ('stt',{}),
         ('product_id',{'func':lambda v,n: v.name,'width':get_width(50)}),
         ('thiet_bi_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('brand_id',{'func':lambda v,n: v.name}),
         ('tracking',{}),
         ('categ_id',{'func':lambda v,n: v.name}),
         ('pn_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('lot_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('location_id',{'func':lambda v,n: v.name_get_1_record(),'write_to_excel':False,'split':[
                 ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'karg':{'stock_type':'tram'}}),         
                 ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'karg':{'stock_type':'phong_may'}}),
                 ('tu',{'is_not_model_field':True,'string':u'Tủ','func':tu_shelf_,'karg':{'stock_type':'tu'}}),
                 ('shelf',{'is_not_model_field':True,'string':u'Shelf','func':tu_shelf_,'karg':{'stock_type':'shelf'},'width':get_width(100)}),
                 ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf','func':tu_shelf_,'karg':{'stock_type':'stt_trong_self'}}),
                 ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'karg':{'stock_type':'slot'}})     
             ]}),
          ('quantity',{'width':get_width(40)}),
                    ]
Export_Para_quants = {
    'exported_model':'stock.quant',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR,
    'gen_domain':gen_domain_stock_quant,
    'search_para':{'order': 'stt asc'},#desc
    }
    
    

def download_quants(dlcv_obj,workbook=None,append_domain=None,sheet_name=None):
    return download_model(dlcv_obj,Export_Para=Export_Para_quants,append_domain=append_domain,workbook=workbook,sheet_name=sheet_name)

def gen_domain_sml(dlcv_obj):
    domain = []
    domain.append(('picking_id','=',dlcv_obj.id))
    return domain
    
FIELDNAME_FIELDATTR_SML = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
#          ('stt',{}),
         ('product_id',{'func':lambda v,n: v.name,'width':get_width(50)}),
#          ('thiet_bi_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
#          ('brand_id',{'func':lambda v,n: v.name}),
#          ('tracking',{}),
#          ('categ_id',{'func':lambda v,n: v.name}),
         ('product_uom_id',{'width':get_width(40),'string':u'ĐVT'}),
         ('qty_done',{'width':get_width(40),'string':u'Số Lượng'}),
         ('pn_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('lot_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
       
#          ('location_id',{'func':lambda v,n: v.name_get_1_record(),'write_to_excel':False,'split':[
#                  ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'karg':{'stock_type':'tram'}}),         
#                  ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'karg':{'stock_type':'phong_may'}}),
#                  ('tu',{'is_not_model_field':True,'string':u'Tủ','func':tu_shelf_,'karg':{'stock_type':'tu'}}),
#                  ('shelf',{'is_not_model_field':True,'string':u'Shelf','func':tu_shelf_,'karg':{'stock_type':'shelf'},'width':get_width(100)}),
#                  ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf','func':tu_shelf_,'karg':{'stock_type':'stt_trong_self'}}),
#                  ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'karg':{'stock_type':'slot'}})     
#              ]}),
                    ]
Export_Para_sml = {
    'exported_model':'stock.move.line',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_SML,
    'gen_domain':gen_domain_sml,
    'search_para':{'order': 'stt asc'},#desc
    }
def download_sml(dlcv_obj,workbook=None,append_domain=None,sheet_name=None):
    return download_model(dlcv_obj,Export_Para=Export_Para_sml,append_domain=append_domain,workbook=workbook,sheet_name=sheet_name)

#######################ML################################

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
    
    for c, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
        is_ml_field = False
        f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
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
                
        split = FIELDATTR.get('split')
        fields = FIELDATTR.get('fields')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        
        
        if is_not_model_field:
            val = False
        else:
            val = getattr(r, f_name)
        one_field_val = a_instance_dict.setdefault(f_name,{})
        one_field_val['val_before_func'] = val
        func = FIELDATTR.get('func',None)
        karg = FIELDATTR.get('karg',{})
        if func:
            val = func(val,needdata,move,ml, **karg)
        print (f_name, val)
        if val == False:
            print ('FALSE',f_name,val)
            val = u''
        one_field_val['val']=val 
        if write_to_excel:
            if is_same:
                if ml_index==0:
                    worksheet.write_merge(row_index, row_index +rowspan-1, col_index,col_index,val,normal_border_style)
            else:
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
        if fields:
            a_instance_dict,writen_column_number_children = add_1_row_squant(worksheet,ml ,fields, row_index, offset_column=col_index  ,f_name_slit_parrent = f_name,needdata=needdata)
            offset_column += writen_column_number_children -1 +  (1 if write_to_excel else 0)
            writen_column_number += writen_column_number_children
            one_field_val['fields'] = a_instance_dict
            col_index +=writen_column_number_children
    return a_instance_dict, writen_column_number



 
# normal_not_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ;align:  vert centre, horiz center;")


def download_model_new_ml(dlcv_obj, Export_Para=None,workbook=None,append_domain=None,sheet_name=None,worksheet=None,row_index=15):
    exported_model= Export_Para['exported_model']
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
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
    squants = request.env[exported_model].search(domain,**order)
    model_fields = request.env[exported_model]._fields
    add_title(worksheet, FIELDNAME_FIELDATTR, model_fields, ROW_TITLE=14, offset_column=0,is_set_width = False)
    for move in squants:#request.env['cvi'].search([]):
        rowspan = len(move.move_line_ids)
        for ml_index, ml in enumerate(move.move_line_ids):
            add_1_row_squant_new_ml(worksheet, move , FIELDNAME_FIELDATTR, row_index, offset_column=0,needdata=needdata,save_ndata=True, ml=ml, ml_index=ml_index,rowspan=rowspan)
            row_index +=1
    return workbook



def ghi_chu_(val,n,move,ml):
    if not val:
        return move.ghi_chu
    else:
        return val
def is_same_(m,ml):
    if m.product_id.tracking == 'none':
        is_same = False
    else:
        is_same = True
    return is_same
def quantity_done_(v,n,m,l):
    if m.product_id.tracking == 'none':
        qty = l.qty_done
    else:
        qty = v
    return qty

FIELDNAME_FIELDATTR_ML = [
         ('move_line_ids.stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_ml_ }),
         ('product_id',{'func':lambda v,n,m,ml: v.name,'width':get_width(50)}),
         ('move_line_ids.pn_id',{'func':lambda v,n,m,ml: v.name,'width':get_width(20),'string':u'PN'}),
         ('quantity_done',{'width':get_width(40),'is_same':is_same_,'func':quantity_done_}),
         ('product_uom',{'func':lambda v,n,m,ml: v.name,'width':get_width(40)}),
         ('move_line_ids.lot_id',{'func':lambda v,n,m,ml: v.name,'width':get_width(20),'string':u'SN'}),
         ('move_line_ids.ghi_chu',{'string':u'Ghi chú','func':ghi_chu_}),
        ]
Export_Para_ml = {
    'exported_model':'stock.move',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_ML,
    'gen_domain':gen_domain_sml,
    'search_para':{'order': 'stt asc'},#desc
    }
def download_ml(dlcv_obj,workbook=None,append_domain=None,sheet_name=None,row_index=0):
    return download_model_new_ml(dlcv_obj,Export_Para=Export_Para_ml,append_domain=append_domain,workbook=workbook,sheet_name=sheet_name,row_index=row_index)

def download_ml_for_bb(dlcv_obj,workbook=None,append_domain=None,sheet_name=None,worksheet=None,row_index=0):
    return download_model_new_ml(dlcv_obj, Export_Para=Export_Para_ml, append_domain=append_domain,
                                 workbook=workbook,
                                 sheet_name=sheet_name,
                                 worksheet=worksheet,
                                 row_index=row_index)





class DownloadQuants(http.Controller):
    @http.route('/web/binary/download_quants',type='http', auth="public")
    def download_quants_by_new_window(self,model, id, **kw):
        model = 'tonkho.downloadquants'
        dlcv_obj = request.env[model].browse(int(id))
        workbook = download_quants(dlcv_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=stockquantsdl_name_%s-date_%s.xls;target=blank' %(dlcv_obj.name,datetime.datetime.now().strftime('%d_%m_%H_%M')))],
            )
        workbook.save(response.stream)
        return response
    
    
    