# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"
    @api.constrains('location_id','quantity')
    def not_allow_negative_qty(self):
        print ('hereeeeeeeee**')
        for r in self:
            if r.location_id.usage =='internal':
                if r.quantity < 0:
                    raise UserError ( u' Không cho phép tạo âm')