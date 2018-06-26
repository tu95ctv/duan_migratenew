# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import  float_compare,float_is_zero
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

# 'stock.move.line'
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    pn = fields.Char(related='lot_id.pn', string=u'Part number')
    stock_quant_id = fields.Many2one('stock.quant',string=u"Lấy vật tư có trong kho")
    tracking = fields.Selection(related='product_id.tracking',string=u'Có SN?', store=True,readonly=True)
    ghi_chu = fields.Text(string=u'Ghi chú')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory',related='move_id.inventory_id',readonly=True)
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],default='tot',string=u'Tình trạng')
    @api.onchange('product_id')
    def qty_done_(self):
        if self.product_id:
            self.qty_done = 1
            self.product_uom_id = self.product_id.uom_id.id
    @api.onchange('qty_done')
    def _onchange_qty_done(self):
        """ When the user is encoding a move line for a tracked product, we apply some logic to
        help him. This onchange will warn him if he set `qty_done` to a non-supported value.
        """
        res = {}
        if self.product_id.tracking == 'serial':
            fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.move_id.product_id.uom_id.rounding)
            if fl > 1:
                message = _('You can only process 1.0 %s for products with unique serial number.') % self.product_id.uom_id.name
                res['warning'] = {'title': _('Warning'), 'message': message}
        return res

    @api.onchange('stock_quant_id')
    def stock_quant_id_change_(self):
        if self.stock_quant_id:
            self.product_id = self.stock_quant_id.product_id
            self.lot_id = self.stock_quant_id.lot_id
            self.location_id = self.stock_quant_id.location_id
#             self.qty_done = 1
    @api.onchange('lot_name')
    def lot_id_when_picking_type(self):
        if self.lot_name:
            lot_id = self.env['stock.production.lot'].search([('name','=',self.lot_name),('product_id','=',self.product_id.id)]).id
            self.lot_id = lot_id
        
        
#     def unlink(self):
#         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#         for ml in self:
#             print ('ml.state',ml.state,ml.product_id.name,ml.qty_done,ml.id)
#             if ml.state in ('done', 'cancel'):
#                 raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
#             # Unlinking a move line should unreserve.
#             if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
#                 try:
#                     self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
#                 except UserError:
#                     if ml.lot_id:
#                         self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
#                     else:
#                         raise
#         moves = self.mapped('move_id')
#         res = super(StockMoveLine, self).unlink()
#         if moves:
#             moves._recompute_state()
#         return res