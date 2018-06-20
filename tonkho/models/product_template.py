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
    thiet_bi_id = fields.Many2one('tonkho.thietbi', string = u'Thiết bị')
    brand_id = fields.Many2one('tonkho.brand',string=u'Hãng sản xuất')
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    quant_ids = fields.One2many('stock.quant', 'product_id',domain=[('location_id.usage','=','internal')],string=u'Trong kho')#domain=[('location_id.usage','=','internal')]
    stock_location_id_selection = fields.Selection('get_stock_for_selection_field_', store=False)
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
#         ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", default='none', required=True)
    def get_stock_for_selection_field_(self):
        locs = self.env['stock.location'].search([('is_kho_cha','=',True)])
        rs = list(map(lambda i:(i.name,i.name),locs))
        return rs
    
    
    
    
    def write(self, vals):
        return super(PT, self.with_context(search_move_line_in_write=1)).write(vals) # vi sao phai lam vay --> de change uom cua PT
    

            
        