# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PN(models.Model):
    _name = 'tonkho.pn'
    name =  fields.Char()
    product_id = fields.Many2one('product.product')
    sn_ids = fields.One2many('stock.production.lot','pn_id')
    
    