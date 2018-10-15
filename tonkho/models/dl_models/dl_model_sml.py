# -*- coding: utf-8 -*-
#######################ML################################
from odoo.addons.tonkho.models.dl_models.dl_model import  download_model,get_width


def stt_(v,needdata): 
    v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
    return v  
def gen_domain_sml(dl_obj):
    domain = []
    domain.append(('picking_id','=',dl_obj.id))
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
#                  ('tram',{'is_not_model_field':True,'string':u'Trạm','func':tu_shelf_,'kargs':{'stock_type':'tram'}}),         
#                  ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy','func':tu_shelf_,'kargs':{'stock_type':'phong_may'}}),
#                  ('tu',{'is_not_model_field':True,'string':u'Tủ','func':tu_shelf_,'kargs':{'stock_type':'tu'}}),
#                  ('shelf',{'is_not_model_field':True,'string':u'Shelf','func':tu_shelf_,'kargs':{'stock_type':'shelf'},'width':get_width(100)}),
#                  ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf','func':tu_shelf_,'kargs':{'stock_type':'stt_trong_self'}}),
#                  ('slot',{'is_not_model_field':True,'string':u'Slot','func':tu_shelf_,'kargs':{'stock_type':'slot'}})     
#              ]}),
                    ]
Export_Para_sml = {
    'exported_model':'stock.move.line',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_SML,
    'gen_domain':gen_domain_sml,
    'search_para':{'order': 'stt asc'},#desc
    }
def download_sml(dl_obj,workbook=None,append_domain=None,sheet_name=None):
    return download_model(dl_obj,Export_Para=Export_Para_sml,append_domain=append_domain,workbook=workbook,sheet_name=sheet_name)