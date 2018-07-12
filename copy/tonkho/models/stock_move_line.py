# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero,_float_check_precision,float_round,float_compare
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

# def float_compare(value1, value2, precision_digits=None, precision_rounding=None):
#     """Compare ``value1`` and ``value2`` after rounding them according to the
#        given precision. A value is considered lower/greater than another value
#        if their rounded value is different. This is not the same as having a
#        non-zero difference!
#        Precision must be given by ``precision_digits`` or ``precision_rounding``,
#        not both!
# 
#        Example: 1.432 and 1.431 are equal at 2 digits precision,
#        so this method would return 0
#        However 0.006 and 0.002 are considered different (this method returns 1)
#        because they respectively round to 0.01 and 0.0, even though
#        0.006-0.002 = 0.004 which would be considered zero at 2 digits precision.
# 
#        Warning: ``float_is_zero(value1-value2)`` is not equivalent to 
#        ``float_compare(value1,value2) == 0``, as the former will round after
#        computing the difference, while the latter will round before, giving
#        different results for e.g. 0.006 and 0.002 at 2 digits precision. 
# 
#        :param int precision_digits: number of fractional digits to round to.
#        :param float precision_rounding: decimal number representing the minimum
#            non-zero value at the desired precision (for example, 0.01 for a 
#            2-digit precision).
#        :param float value1: first value to compare
#        :param float value2: second value to compare
#        :return: (resp.) -1, 0 or 1, if ``value1`` is (resp.) lower than,
#            equal to, or greater than ``value2``, at the given precision.
#     """
#     print ('precision_rounding',precision_rounding)
#     rounding_factor = _float_check_precision(precision_digits=precision_digits,
#                                              precision_rounding=precision_rounding)
#     print ('rounding_factor',rounding_factor)
#     print ("value1,value2",value1,value2)
#     value1 = float_round(value1, precision_rounding=rounding_factor)
#     value2 = float_round(value2, precision_rounding=rounding_factor)
#     delta = value1 - value2
#     print ("value1,value2,delta,float_is_zero(delta, precision_rounding=rounding_factor)",value1,value2,delta,float_is_zero(delta, precision_rounding=rounding_factor))
#     if float_is_zero(delta, precision_rounding=rounding_factor): return 0
#     return -1 if delta < 0.0 else 1
# 'stock.move.line'
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
#     lot_id = fields.Many2one('stock.production.lot', 'Lot',required=True)
    pn = fields.Char(related='lot_id.pn', string=u'Part number',readonly=False,store=False)
    stock_quant_id = fields.Many2one('stock.quant', string=u"Lấy vật tư có trong kho")
    tracking = fields.Selection(related='product_id.tracking',string=u'Có SN hay không', store=False)
    ghi_chu = fields.Text(string=u'Ghi chú vật tư')
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
#             fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.move_id.product_id.uom_id.rounding)#original
            print ("***self.move_id.product_id.uom_id.rounding",self.move_id.product_id.uom_id.rounding,'self.move_id.product_id.uom_id',self.move_id.product_id.uom_id,'self.move_id.product_id',self.move_id.product_id,'self.move_id',self.move_id)
            fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.product_id.uom_id.rounding)
            #original:
            print ('fl',fl,'self.qty_done',self.qty_done)
            if fl !=0:# fl=1 nếu là băng nhau,-1 nếu khác nhau
            # để tránh cảnh báo: You can only process 1.0 Card for products with unique serial number.
#             if fl > 1:
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
#     @api.onchange('lot_name')
#     def lot_id_when_picking_type(self):
#         if self.lot_name:
#             lot_id = self.env['stock.production.lot'].search([('name','=',self.lot_name),('product_id','=',self.product_id.id)]).id
#             self.lot_id = lot_id
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