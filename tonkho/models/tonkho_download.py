# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
class DownloadQuants(models.TransientModel):
    _inherit = "downloadwizard.download"
    @api.multi
    def gen_pick_func(self): 
        rs = super(DownloadQuants, self).gen_pick_func()
        pick_func = {'stock.quant':download_quants,'product.product':download_product}
        rs.update(pick_func)
        return rs
