# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero,_float_check_precision,float_round,float_compare
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
#     lot_id = fields.Many2one('stock.production.lot', 'Lot',required=True)
    pn = fields.Char(related='lot_id.pn', string=u'Part number',readonly=False,store=False)
    pn_id = fields.Many2one('tonkho.pn',related = 'lot_id.pn_id')
    stock_quant_id = fields.Many2one('stock.quant', string=u"Lấy vật tư có trong kho")
    tracking = fields.Selection(related='product_id.tracking',string=u'Có SN hay không', store=False)
    ghi_chu = fields.Text(string=u'Ghi chú vật tư')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory',related='move_id.inventory_id',readonly=True)
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')], default='tot', string=u'Tình trạng',required=True)
    ref_picking_id_or_inventory_id = fields.Char(compute='ref_picking_id_or_inventory_id_', store=True,string=u'Phiếu tham chiếu')
#     state = fields.Selection(related='move_id.state', store=True)

    
    move_line_dest_ids = fields.Many2many(
        'stock.move.line', 'stock_move_line_move_line_rel', 'move_line_orig_id', 'move_line_dest_id', 'Destination Move Lines',
        copy=False,
        help="Optional: next stock move when chaining them")
    move_line_orig_ids = fields.Many2many(
        'stock.move.line', 'stock_move_line_move_line_rel', 'move_line_dest_id', 'move_line_orig_id', 'Original Move Lines',
        copy=False,
        help="Optional: previous stock move when chaining them")
    origin_returned_move_id = fields.Many2one('stock.move.line', 'Origin return move', copy=False, help='Move that created the return move')
    returned_move_ids = fields.One2many('stock.move.line', 'origin_returned_move_id', 'All returned moves', help='Optional: all returned moves created from this move')
    stt = fields.Integer()
    inventory_line_id = fields.Many2one('stock.inventory.line')
    
    def _action_done(self):
        print ('888',self._context,'action_done_from_stock_inventory' in self._context)
        if 'action_done_from_stock_inventory' in self._context:
            self =  self.with_context(update_inventory={'stt':self.stt, 'inventory_line_id':self.inventory_line_id.id})
        return super(StockMoveLine,self )._action_done()
    
    @api.onchange('location_id')
    def location_id_onchange(self):
#         print ('self.env.context.get()',self.env.context.get('ban_giao_or_nghiem_thu'))
        if self.env.context.get('ban_giao_or_nghiem_thu') =='TDTT':
            self.location_dest_id = self.location_id
#             return {
#                     'readonly': {
#                         'location_dest_id': "1"
#                        
#                     },
#                     'attrs': {
#                         'location_dest_id': {'readonly':[True]}
#                     },
#                     
#                     
#                     'value': {
#                         'location_dest_id': self.location_id,
#                         
#                     }
#                 }
#         return {'location_dest_id':}
    @api.onchange('lot_id')
    def lot_id_onchange(self):
        if self.lot_id:
            self.tinh_trang = self.lot_id.tinh_trang
        
    @api.depends('inventory_id','picking_id.name')
    def ref_picking_id_or_inventory_id_(self):
        for r in self:
            ref = u'INV: ' + r.inventory_id.name if r.inventory_id else r.picking_id.name
            r.ref_picking_id_or_inventory_id = ref
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