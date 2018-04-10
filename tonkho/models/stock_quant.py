# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"
    pn = fields.Char(related='lot_id.pn')
    @api.constrains('location_id','quantity')
    def not_allow_negative_qty(self):
        print ('hereeeeeeeee**')
        for r in self:
            if r.location_id.usage =='internal':
                if r.quantity < 0:
                    raise UserError ( u' Không cho phép tạo âm')