# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero,_float_check_precision,float_round,float_compare
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    pn_id = fields.Many2one('tonkho.pn',related = 'lot_id.pn_id',string=u'Part number')
    stock_quant_id = fields.Many2one('stock.quant', string=u"Lấy vật tư có trong kho")
    tracking = fields.Selection(related='product_id.tracking',string=u'Có SN hay không', store=False)
    ghi_chu = fields.Text(string=u'Ghi chú vật tư')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory',related='move_id.inventory_id',readonly=True)
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')], default='tot', string=u'Tình trạng',required=True)
    ref_picking_id_or_inventory_id = fields.Char(compute='ref_picking_id_or_inventory_id_', store=True,string=u'Phiếu tham chiếu')

    
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
        if 'action_done_from_stock_inventory' in self._context:
            self =  self.with_context(update_inventory={'stt':self.stt, 'inventory_line_id':self.inventory_line_id.id})
        return super(StockMoveLine,self )._action_done()
    
    
    @api.onchange('lot_id')
    def lot_id_onchange(self):
        if self.lot_id.tinh_trang:
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
    def _onchange_qty_done(self):# ghi đè để tránh cảnh báo: You can only process 1.0 Card for products with unique serial number.
        """ When the user is encoding a move line for a tracked product, we apply some logic to
        help him. This onchange will warn him if he set `qty_done` to a non-supported value.
        """
        res = {}
        if self.product_id.tracking == 'serial':
#             fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.move_id.product_id.uom_id.rounding)#original
            fl =  float_compare(self.qty_done, 1.0, precision_rounding=self.product_id.uom_id.rounding)
            #original:
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
