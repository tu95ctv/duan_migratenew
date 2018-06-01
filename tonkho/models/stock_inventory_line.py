# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare



class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    categ_id = fields.Many2one('product.category', related='product_id.categ_id',store=True)
    thiet_bi_id = fields.Many2one('tonkho.thietbi', related='product_id.thiet_bi_id',store=True)
    brand_id = fields.Many2one('tonkho.brand', related='product_id.brand_id',store=True)
    pn = fields.Char(related = 'prod_lot_id.pn',store=True)
    stt = fields.Integer()
    
    