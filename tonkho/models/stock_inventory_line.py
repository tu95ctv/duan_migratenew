# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    categ_id = fields.Many2one('product.category', related='product_id.categ_id',store=True,string=u'Nhóm')
    thiet_bi_id = fields.Many2one('tonkho.thietbi', related='product_id.thiet_bi_id',store=True)
    brand_id = fields.Many2one('tonkho.brand', related='product_id.brand_id',store=True)
#     pn = fields.Char(related = 'prod_lot_id.pn',store=True)
    pn_id = fields.Many2one('tonkho.pn',related = 'prod_lot_id.pn_id',store=True)
    pn = fields.Char(related = 'prod_lot_id.pn',store=True)
    stt = fields.Integer(string=u'STT')
#     id_of_product_id =  fields.Integer(related='product_id.id')
    tracking =  fields.Selection(related='product_id.tracking', store=True,string=u'Có SN hay không')
    ghi_chu = fields.Text(string=u'Ghi chú')
    barcode_sn = fields.Char(related = 'prod_lot_id.barcode_sn',store=True)
    quant_ids =  fields.One2many('stock.quant','inventory_line_id')
    
    def _get_move_values(self,*arg,**karg):
        rs = super(InventoryLine, self)._get_move_values(*arg,**karg)
#         rs['stt'] = self.stt
        rs['move_line_ids'][0][2]['stt'] = self.stt#self._context['stt']
        rs['move_line_ids'][0][2]['inventory_line_id'] = self.id
        return rs
        
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('context_in_create'):
            return False
        return super(InventoryLine, self).search(args, offset, limit, order, count=count)
    @api.model
    def create(self, values):
#         values.pop('product_name', False)
#         if 'product_id' in values and 'product_uom_id' not in values:
#             values['product_uom_id'] = self.env['product.product'].browse(values['product_id']).uom_id.id
#         existings = self.search([
#             ('product_id', '=', values.get('product_id')),
#             ('inventory_id.state', '=', 'confirm'),
#             ('location_id', '=', values.get('location_id')),
#             ('partner_id', '=', values.get('partner_id')),
#             ('package_id', '=', values.get('package_id')),
#             ('prod_lot_id', '=', values.get('prod_lot_id'))])
#         res = super(InventoryLine, self).create(values)
#         if existings:
#             raise UserError(_("You cannot have two inventory adjustements in state 'in Progress' with the same product "
#                               "(%s), same location (%s), same package, same owner and same lot. Please first validate "
#                               "the first inventory adjustement with this product before creating another one.") % (res.product_id.display_name, res.location_id.name))
        
        res = super(InventoryLine, self.with_context(context_in_create=True)).create(values)
        return res
    
    
    