# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"
    pn = fields.Char(related='lot_id.pn')
    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
#         change_default=True, default=_get_default_category_id,
         help="Select category for the current product",related='product_id.categ_id',store=True)
    
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", related='product_id.tracking',store=True)
    
    @api.constrains('location_id','quantity')
    def not_allow_negative_qty(self):
        for r in self:
            if not r.location_id.cho_phep_am:
                if r.quantity < 0:
                    raise UserError ( u' Không cho phép tạo âm')
    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [
            ('product_id', '=', self.product_id.id),
#             '|', ('location_id', '=', self.location_id.id),
#             ('location_dest_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            ('package_id', '=', self.package_id.id)]
        return action