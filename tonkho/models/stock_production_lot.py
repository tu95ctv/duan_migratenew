# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression
import re


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    _sql_constraints = [
#         ('name_ref_uniq', 'unique (name, product_id)', 'The combination of serial number and product must be unique !'),
#         ('name_ref_uniq', 'unique (name, product_id,barcode_sn)', 'The combination of serial number and product must be unique !'),
        ('name_ref_uniq', 'unique (name)', 'The serial number must be unique !'),

    ]
#     _rec_name = 'complete_name'
    name = fields.Char(
        'Lot/Serial Number', 
#         default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        default = False,
        required=True, help="Unique Lot/Serial Number")
    ghi_chu = fields.Text(string=u'Ghi chú từ dòng điều chuyển',
#                           compute='ghi_chu_',
#                           store=True
                          )
#     @api.depends('move_line_ids.ghi_chu','move_line_ids.state')
#     def ghi_chu_(self):
#         for r in self:
#             if isinstance(r.id, int):
# #                 move_line_ids = r.move_line_ids.filtered(lambda r: r.state=='done')
#                 move_line_ids = self.env['stock.move.line'].search([('lot_id','=',r.id),('ghi_chu','!=',False),('state','=','done')],limit=1,order='id desc')
#                 if move_line_ids:
#                     r.ghi_chu =move_line_ids.ghi_chu
                    
                    
                    
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi Chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    move_line_ids = fields.One2many('stock.move.line','lot_id')
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],
                                  default='tot',
#                                 compute='tinh_trang_depend_move_line_ids_',
                                  store=True,
                                   string=u'Tình trạng')
    

    
#     tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],default='tot',store=True, string=u'Tình trạng')
    barcode_sn = fields.Char()
    id_ke_toan = fields.Char(string=u'ID kế toán')
    the_tai_san = fields.Char(string=u'Thẻ tài sản')
    ngay_su_dung = fields.Date(string=u'Ngày sử dụng')
#     context = fields.Char(compute='context_')
    pn = fields.Char(related='product_id.pn',string=u'Part number',store=True)
    name_replace = fields.Char(compute='name_replace_',store=True)
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            name_replace = re.sub('[-_ \s]','',name)
        else:
            name_replace = ''
        recs = self.search(['|',('name', operator, name), ('name_replace', operator, name_replace)] + args, limit=limit)
        return recs.name_get()
    
    
    @api.depends('name')
    def name_replace_(self):
        for r in self:
            if r.name:
                r.name_replace = re.sub('[-_ \s]','',r.name)

    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('lot_id', '=', self.id)]
        return action

    
#     @api.depends('move_line_ids.tinh_trang','move_line_ids.state')
#     @api.constrains('move_line_ids.tinh_trang','move_line_ids.state')
#     def tinh_trang_depend_move_line_ids_(self):
#         for r in self:
#             if isinstance(r.id, int):
#                 move_line_ids = self.env['stock.move.line'].search([('lot_id','=',r.id),('state','=','done')],limit=1,order='id desc')
#                 if move_line_ids:
#                     r.tinh_trang =move_line_ids[-1].tinh_trang
                    
                    
                    
                    
   
                
                
