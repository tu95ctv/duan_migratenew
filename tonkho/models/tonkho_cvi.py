# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.exceptions import UserError
class Cvi(models.Model):
    _inherit = 'cvi'
    thiet_bi_id = fields.Many2one('tonkho.thietbi', string = u'Thiết bị')
    categ_id = fields.Many2one(
        'product.category', u'Nhóm')
    
    @api.onchange('thiet_bi_id')
    def thiet_bi_id_oc_(self):
        if not self.categ_id:
            self.categ_id = self.thiet_bi_id.categ_id
            
            
    @api.onchange('cvi_id')
    def cvi_id_oc_(self):
        self.categ_id = self.cvi_id.categ_id
        self.thiet_bi_id = self.cvi_id.thiet_bi_id
            