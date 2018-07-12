# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
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
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    # THÊM VÀO ĐỂ COI DỊCH CHUYỂN KHO, KHÔNG PHẢI KẾ THỪA
    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('lot_id', '=', self.id)]
        return action
     
    @api.depends('move_line_ids.tinh_trang','move_line_ids.state')
    def tinh_trang_depend_move_line_ids_(self):
        for r in self:
            move_line_ids = r.move_line_ids.filtered(lambda r: r.state=='done')
            if move_line_ids:
                r.tinh_trang =move_line_ids[-1].tinh_trang
     
    @api.depends('move_line_ids.ghi_chu','move_line_ids.state')
    def ghi_chu_(self):
        for r in self:
            move_line_ids = r.move_line_ids.filtered(lambda r: r.state=='done')
            print ('***move_line_ids',move_line_ids)
            if move_line_ids:
                r.ghi_chu =move_line_ids[-1].ghi_chu
            else:
                print ('chua con  move_line_ids có trang thai done nao ca')
            
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