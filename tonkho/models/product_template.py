# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare


class ThietBi(models.Model):
    _name = 'tonkho.thietbi'
    name = fields.Char()
class Brand(models.Model):
    _name = 'tonkho.brand'
    name = fields.Char()

class PT(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = 'product.template'
    type = fields.Selection(selection_add=[],default = 'product')
    thiet_bi_id = fields.Many2one('tonkho.thietbi', string = u'Thiết Bị')
    brand_id = fields.Many2one('tonkho.brand',string=u'Hãng sản xuất')
    department_id = fields.Many2one('hr.department',string=u'Đơn vị tạo',default= lambda self:self.env.user.department_id)
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi Chú Ban Đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi Chú Ngày Nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi Chú Ngày Xuất')
    
#     @api.multi
    def write(self, vals):
        #You can not change the unit of measure of a product that has already been used in a done stock move
        return super(PT, self.with_context(search_move_line_in_write=1)).write(vals)
    

            
        