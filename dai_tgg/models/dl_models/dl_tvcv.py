# -*- coding: utf-8 -*-
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from openerp.http import request
import xlwt
from odoo.exceptions import UserError
from copy import deepcopy


def get_width(num_characters):
    return int((1+num_characters) * 256)

def stt_(v,needdata): 
    v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
    return v  
FIELDNAME_FIELDATTR_quants = [
         ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('name',{'width':get_width(40)}),
          ('diem',{'width':get_width(40)}),
          ('don_vi',{})
                    ]
Export_Para_quants = {
    'exported_model':'tvcv',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_quants,
#     'gen_domain':gen_domain_stock_quant,
#     'search_para':{'order': 'stt asc'},#desc
    }
    
def download_tvcv1(dl_obj,append_domain = []):
    if not dl_obj.is_moi_sheet_moi_loai:
#         return download_quants_chung_sheet(dl_obj)
        filename = 'tvcv'
        name = "%s%s" % (filename, '.xls')
        workbook =  download_model(dl_obj,
                             Export_Para=Export_Para_quants,
                             append_domain=append_domain
                            )
    else:
        filename = 'tvcv_cate'
        name = "%s%s" % (filename, '.xls')
        Quant = request.env['tvcv']#.search([])
        cates = Quant.search(append_domain).mapped('cong_viec_cate_id')
        workbook = xlwt.Workbook()
        for cate in cates:
            Export_Para_quants_copy = deepcopy(Export_Para_quants)
            if append_domain:
                domain =[('cong_viec_cate_id','=',cate.id)]
                domain.extend(append_domain)
            download_model(dl_obj,
                         Export_Para=Export_Para_quants_copy,
                         append_domain=domain,
                         workbook=workbook,
                         sheet_name=cate.name)
    
    return workbook,name
        
    


# def download_quants_chung_sheet(dl_obj,workbook=None,
#                                 append_domain=None,
#                                 sheet_name=None):
#     filename = 'quants-%s'%dl_obj.parent_location_id.name
#     name = "%s%s" % (filename, '.xls')
#     wb =  download_model(dl_obj,
#                          Export_Para=Export_Para_quants,
#                          append_domain=append_domain,
#                          workbook=workbook,
#                          sheet_name=sheet_name)
#     return wb,name
# # def download_quants_moi_cage_moi_sheet(dl_obj):
# #     filename = 'quants_moi_cate_moi_sheet%s'%dl_obj.parent_location_id.name
# #     name = "%s%s" % (filename, '.xls')
# #     Quant = request.env['stock.quant']#.search([])
# #     cates = Quant.search([]).mapped('categ_id')
# #     workbook = xlwt.Workbook()
# #     for cate in cates:
# #         download_quants_chung_sheet(dl_obj,workbook=workbook,append_domain=[('categ_id','=',cate.id)],sheet_name=cate.name)
# #     return workbook,name
# def download_quants_moi_cage_moi_sheet(dl_obj):
#     filename = 'quants_moi_cate_moi_sheet%s'%dl_obj.parent_location_id.name
#     name = "%s%s" % (filename, '.xls')
#     Quant = request.env['stock.quant']#.search([])
#     cates = Quant.search([]).mapped('categ_id')
#     workbook = xlwt.Workbook()
#     for cate in cates:
# #         download_quants_chung_sheet(dl_obj,workbook=workbook,append_domain=[('categ_id','=',cate.id)],sheet_name=cate.name)
#         download_model(dl_obj,
#                          Export_Para=Export_Para_quants,
#                          append_domain=[('categ_id','=',cate.id)],
#                          workbook=workbook,
#                          sheet_name=cate.name)
#     return workbook,name

