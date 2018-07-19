# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name, product_id, barcode)', 'The combination of serial number and product must be unique !'),
    ]
    _rec_name = 'complete_name'
    name = fields.Char(
        'Lot/Serial Number', 
#         default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        default = False,
        required=True, help="Unique Lot/Serial Number")
     
    pn = fields.Char(string=u'Part Number')
#     ghi_chu = fields.Text(string=u'Ghi chú',store=True)
    ghi_chu = fields.Text(string=u'Ghi chú',compute='ghi_chu_',store=True)
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi Chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    pn_id = fields.Many2one('tonkho.pn')
    move_line_ids = fields.One2many('stock.move.line','lot_id')
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],default='tot',compute='tinh_trang_depend_move_line_ids_',store=True, string=u'Tình trạng')
#     tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],default='tot',store=True, string=u'Tình trạng')
    # THÊM VÀO ĐỂ COI DỊCH CHUYỂN KHO, KHÔNG PHẢI KẾ THỪA
    barcode_sn = fields.Char()
    complete_name = fields.Char(compute='complete_name_',store=True)
    trig_field = fields.Boolean()
    @api.depends('barcode_sn','name','trig_field')
    def complete_name_(self):
        for r in self:
            if r.name =='unknown':
                if r.barcode_sn:
                    r.complete_name = u'bc: ' + r.barcode_sn
                
            else:
                r.complete_name = r.name
        
    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('lot_id', '=', self.id)]
        return action

    @api.depends('move_line_ids.tinh_trang','move_line_ids.state')
    def tinh_trang_depend_move_line_ids_(self):
        for r in self:
            if isinstance(r.id, int):
                move_line_ids = self.env['stock.move.line'].search([('lot_id','=',r.id),('ghi_chu','!=',False),('state','=','done')],limit=1,order='id desc')
                if move_line_ids:
                    r.tinh_trang =move_line_ids[-1].tinh_trang
     
#     @api.depends('move_line_ids.ghi_chu','move_line_ids.state')
#     def ghi_chu_(self):
#         for r in self:
#             move_line_ids = r.move_line_ids.filtered(lambda r: r.state=='done')
#             if move_line_ids:
#                 r.ghi_chu =move_line_ids[-1].ghi_chu

    @api.depends('move_line_ids.ghi_chu','move_line_ids.state')
    def ghi_chu_(self):
        for r in self:
            if isinstance(r.id, int):
#                 move_line_ids = r.move_line_ids.filtered(lambda r: r.state=='done')
                move_line_ids = self.env['stock.move.line'].search([('lot_id','=',r.id),('ghi_chu','!=',False),('state','=','done')],limit=1,order='id desc')
                if move_line_ids:
                    r.ghi_chu =move_line_ids.ghi_chu
                
        
            
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        location_id = self._context.get('d4_location_id')
        print ('location_id',location_id)
        if location_id:
            location_id_object = self.env['stock.location'].browse([location_id])
            if location_id_object.usage == 'internal':
                def filter_lots(r):
                    quants = self.env['stock.quant'].search([('location_id','=',location_id),('lot_id','=',r.id),('quantity','>',0)])
                    print ('location_id',location_id,'r.id',r.id,'quants',quants,'len(quants)',len(quants))
                    if len(quants) >0 :
                        return True
                    else:
                        return False
                if args ==None:
                    args = []
                domain = expression.AND([[('name',operator,name)],args])
                lots = self.env["stock.production.lot"].search(domain, limit=limit)
                lots = lots.filtered(filter_lots )
                return lots.name_get()
        return super(StockProductionLot,self).name_search( name, args=args, operator=operator, limit=limit)