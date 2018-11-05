# -*- coding: utf-8 -*-
from odoo.addons.tonkho.models.dl_models.dl_model import  download_model
from openerp.http import request
import xlwt
from odoo.exceptions import UserError
from copy import deepcopy

def get_width(num_characters):
    return int((1+num_characters) * 256)


def stt_(v,needdata): 
    v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
    return v      

def tu_shelf_(v,needdata, stock_type=None):
    location_id = needdata['a_instance_dict']['location_id']['val_before_func']
    l_id = request.env['stock.location'].search([('id','parent_of',location_id.id),('stock_type','=',stock_type)])
    return l_id.name

def gen_domain_stock_quant(dl_obj):
    domain = []
    if dl_obj.parent_location_id:
        domain.append(('location_id','child_of',dl_obj.parent_location_id.id))
    return domain
def tracking_(v,needdata):
    adict = {'serial':u'Có SN','none':u'Không có SN'}
    return adict[v]
    
def download_quants(dl_obj,append_domain = []):
    
    FIELDNAME_FIELDATTR_quants = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
         ('stt',{'skip_field':not dl_obj.is_not_skip_field_stt}),
         ('product_id',{'func':lambda v,n: v.name,'width':get_width(50)}),
         ('thiet_bi_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('brand_id',{'func':lambda v,n: v.name}),
         ('tracking',{'func':tracking_}),
         ('categ_id',{'func':lambda v,n: v.name,'width':get_width(20) }),
         ('pn_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('lot_id',{'func':lambda v,n: v.name,'width':get_width(20)}),
         ('location_id',{'func':lambda v,n: v.name_get_1_record(),'write_to_excel':False,'split':[
                 ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'kargs':{'stock_type':'tram'}}),         
                 ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'kargs':{'stock_type':'phong_may'}}),
                 ('tu',{'is_not_model_field':True,'string':u'Tủ','func':tu_shelf_,'kargs':{'stock_type':'tu'}}),
                 ('shelf',{'is_not_model_field':True,'string':u'Shelf','func':tu_shelf_,'kargs':{'stock_type':'shelf'}}),
                 ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf','func':tu_shelf_,'kargs':{'stock_type':'stt_trong_self'}}),
                 ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'kargs':{'stock_type':'slot'}})     
             ]}),
          ('quantity',{'width':get_width(40)}),
                    ]
    Export_Para_quants = {
        'exported_model':'stock.quant',
        'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_quants,
        'gen_domain':gen_domain_stock_quant,
        'search_para':{'order': 'stt asc'},#desc
        }
    
    if not dl_obj.is_moi_sheet_moi_loai:
        filename = 'quants_%s'%dl_obj.parent_location_id.name
        name = "%s%s" % (filename, '.xls')
        workbook =  download_model(dl_obj,
                             Export_Para=Export_Para_quants,
                             append_domain=append_domain
                            )
    else:
        filename = 'quants_cate_%s'%dl_obj.parent_location_id.name
        name = "%s%s" % (filename, '.xls')
        Quant = request.env['stock.quant']#.search([])
        cates = Quant.search(append_domain).mapped('categ_id')
        workbook = xlwt.Workbook()
        for cate in cates:
            Export_Para_quants_copy = deepcopy(Export_Para_quants)
            if append_domain:
                domain =[('categ_id','=',cate.id)]
                domain.extend(append_domain)
            download_model(dl_obj,
                         Export_Para=Export_Para_quants_copy,
                         append_domain=domain,
                         workbook=workbook,
                         sheet_name=cate.name)
    
    return workbook,name
        
    


