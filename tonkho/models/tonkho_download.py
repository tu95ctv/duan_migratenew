# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
class DownloadQuants(models.TransientModel):
    _inherit = "downloadwizard.download"
    
    parent_location_id =  fields.Many2one('stock.location',
                                        default=lambda self:self.env.user.department_id.default_location_id.id, string=u'Kho cha dự phòng'
                                          )
    parent_location_runing_id =  fields.Many2one('stock.location',
                                                default=lambda self:self.env.user.department_id.default_location_running_id.id,
                                                 string=u'Kho đang chạy'
                                                 )
    
    is_xuat_dc =  fields.Boolean(u'Xuất cột số lượng điều chỉnh',default=True)
    is_xuat_kho_dc =  fields.Boolean(u'Xuất cột kho điều chỉnh',default=True)
#     test =  fields.Text()
    @api.multi
    def gen_pick_func(self): 
        rs = super(DownloadQuants, self).gen_pick_func()
        pick_func = {'stock.quant':download_quants,'product.product':download_product}
        rs.update(pick_func)
        return rs
    @api.multi
    def gen_pick_model_name(self): 
        adict =  {'stock.quant':u'Kho','product.product':u'Vật tư'}
        rs = super(DownloadQuants, self).gen_pick_model_name()
        rs.update(adict)
        return rs
    