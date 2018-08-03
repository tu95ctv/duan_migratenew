# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
import datetime
from odoo.tools.misc import xlwt
from odoo.addons.dai_tgg.mytools import  convert_date_odoo_to_str_vn_date
from odoo.exceptions import UserError
dlcv_obj_global = None
def get_width(num_characters):
    return int((1+num_characters) * 256)
request_or_self_global = None
normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;borders: left thin,right thin, top thin, bottom thin")
# needdata ={}
def add_title(worksheet,FIELDNAME_FIELDATTR,cvi_fields,ROW_TITLE=0, offset_column=0):
    header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ; pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
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
            field = cvi_fields[f_name]
            f_string = field.string
        if write_to_excel:
            worksheet.write(ROW_TITLE, column_index, f_string, header_bold_style)
            writen_column_number += 1
            width  = FIELDATTR.get('width')
            if not width :
                width = get_width(len(f_string))
            worksheet.col(column_index).width = width
            column_index +=1
        else:
            pass
        if split:
            writen_column_number_child = add_title(worksheet,split, cvi_fields,ROW_TITLE=ROW_TITLE, offset_column=column_index)
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
        if f_name_slit_parrent:
            val = getattr(r, f_name_slit_parrent)
        else:
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
def stt_(v,needdata): 
#     print ("needdata['a_instance_dict_last']",needdata['a_instance_dict_last'])
    v = needdata['a_instance_dict']['stt']['val']  +1   
    return v      
    
def tu_shelf_(v,needdata, stock_type=None):
    location_id = needdata['a_instance_dict']['location_id']['val_before_func']
    l_id = request.env['stock.location'].search([('id','parent_of',location_id.id),('stock_type','=',stock_type)])
    return l_id.name

def gen_domain_stock_quant(dlcv_obj):
    domain = []
    if dlcv_obj.parent_location_id:
        domain.append(('location_id','child_of',dlcv_obj.parent_location_id.id))
    return domain
def pr_running_quant_(v,n,parent_location_id='parent_location_id'):
    domain_quant = [('product_id','=',n['a_instance_dict']['id']['val']),('location_id','child_of',getattr(dlcv_obj_global, parent_location_id).id)]
    Quant = request.env['stock.quant']
#     print (Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
#     quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
#     print ('quants_res',quants_res)
#     raise UserError('kaka')
#     rs = self.env['stock.quant'].read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id')
    print (Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
    try:
        item = Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id')[0]
        quant = item['quantity']
    except IndexError:
        quant = 0
    print ('quant',quant)
    return quant
FIELDNAME_FIELDATTR = [
             ('stt',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
             ('product_id',{'func':lambda v,n: v.name}),
             ('location_id',{'func':lambda v,n: v.name_get_1_record(),'write_to_excel':False,'split':[
                     ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'karg':{'stock_type':'tram'}}),         
                     ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'karg':{'stock_type':'phong_may'}}),
                     ('tu',{'is_not_model_field':True,'string':u'Tủ','func':tu_shelf_,'karg':{'stock_type':'tu'}}),
                     ('shelf',{'is_not_model_field':True,'string':u'Shelf','func':tu_shelf_,'karg':{'stock_type':'shelf'}}),
                     ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf','func':tu_shelf_,'karg':{'stock_type':'stt_trong_self'}}),
                     ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'karg':{'stock_type':'slot'}})     
                 ]}),
              ('quantity',{'width':get_width(40)}),
                        ]
Export_Para_quants = {
    'exported_model':'stock.quant',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR,
    'gen_domain':gen_domain_stock_quant,
    }
FIELDNAME_FIELDATTR_PRODUCT = [
             ('stt',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
             ('id',{}),
             ('name',{}),
             ('categ_id',{'func':lambda v,n: v.name}),
             ('pr_running_quant',{'is_not_model_field':True,'func':pr_running_quant_,'karg':{'parent_location_id':'parent_location_runing_id'}}),
             ('pr_prepare_quant',{'is_not_model_field':True,'func':pr_running_quant_}),
             
             
#              ('location_id',{'func':lambda v,n: v.name_get_1_record(),'write_to_excel':False,'split':[
#                      ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'karg':{'stock_type':'tram'}}),         
#                      ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'karg':{'stock_type':'phong_may'}}),
#                      ('tu',{'is_not_model_field':True,'string':u'Tủ','func':tu_shelf_,'karg':{'stock_type':'tu'}}),
#                      ('shelf',{'is_not_model_field':True,'string':u'Shelf','func':tu_shelf_,'karg':{'stock_type':'shelf'}}),
#                      ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf','func':tu_shelf_,'karg':{'stock_type':'stt_trong_self'}}),
#                      ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'karg':{'stock_type':'slot'}})     
#                  ]}),
#               ('quantity',{'width':get_width(40)}),
                        ]

Export_Para_pr = {
    'exported_model':'product.product',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_PRODUCT,
    'gen_domain':None,
    'search_para':{'order': 'id asc'},#desc
    }

def download_product(dlcv_obj,request_or_self = request):
    return download_quants(dlcv_obj,request_or_self = request_or_self, context = None,Export_Para=Export_Para_pr)


def download_quants(dlcv_obj,request_or_self = request,context = None, Export_Para=Export_Para_quants):
    global dlcv_obj_global
    dlcv_obj_global = dlcv_obj
    exported_model= Export_Para['exported_model']
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
    gen_domain= Export_Para.get('gen_domain')
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'anh con no em',cell_overwrite_ok=True)
    worksheet.write(1,1,u'Họ và Tên',normal_border_style_not_border)
    needdata = {'a_instance_dict':{'stt':{'val':0}}}
    cvi_fields = request_or_self.env[exported_model]._fields
    ROW_TITLE = 0
    OFFSET_COLUMN = 0
    add_title(worksheet, FIELDNAME_FIELDATTR, cvi_fields, ROW_TITLE=ROW_TITLE, offset_column=OFFSET_COLUMN)
    if gen_domain:
        domain = gen_domain(dlcv_obj)
    else:
        domain = []
    order = Export_Para.get('search_para',{})
    squants = request_or_self.env[exported_model].search(domain,**order)
    row_index = ROW_TITLE + 1
    for r in squants:#request.env['cvi'].search([]):
        add_1_row_squant(worksheet,r, FIELDNAME_FIELDATTR, row_index, offset_column=OFFSET_COLUMN,needdata=needdata,save_ndata=True)
        row_index +=1
    return workbook



class DownloadQuants(http.Controller):
    @http.route('/web/binary/download_quants',type='http', auth="public")
    def download_quants(self,model, id, **kw):
        model = 'tonkho.downloadquants'
        dlcv_obj = request.env[model].browse(int(id))
        workbook = download_quants(dlcv_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=stockquantsdl_name_%s-date_%s.xls;target=blank' %(dlcv_obj.name,datetime.datetime.now().strftime('%d_%m_%H_%M')))],
            )
        workbook.save(response.stream)
        return response
    
    
    