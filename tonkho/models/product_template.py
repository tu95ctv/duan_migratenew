# -*- coding: utf-8 -*-
from odoo import models, fields, api#,tools
from odoo.exceptions import UserError#, except_orm
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
import psycopg2
from unidecode import unidecode
from odoo.addons.dai_tgg.mytools import name_khong_dau_compute
# import itertools
# from odoo.addons.product.models.product_template import  ProductTemplate
# class Categ(models.Model):
#     _inherit = 'product.category'
#     stt_for_report = fields.Integer()
# 
# class PN(models.Model):
#     _name = 'tonkho.pn'
#     _sql_constraints = [
#         ('name_ref_uniq', 'unique (name, product_id)', 'The combination of pn and product must be unique !'),
#     ]
#     name = fields.Char(required=True)
#     product_id = fields.Many2one('product.product',required=True,ondelete='cascade')
#     sn_ids = fields.One2many('stock.production.lot','pn_id',string='Serial numbers')
#     running_or_prepare = fields.Selection([('running',u'Đang chạy'),('prepare',u'Dự phòng')])
# #     import_location_id = fields.Many2one('stock.location')
#     tram_ltk_tao = fields.Boolean()
#     dang_chay_tao = fields.Boolean()
#     du_phong_tao = fields.Boolean()
#     
# # class PNCon(models.Model):
# #     _name = 'tonkho.pncon'
# #     _inherits = {'tonkho.pn': 'pn_id'}
# #     name2 = fields.Char()
# class ThietBi(models.Model):
#     _name = 'tonkho.thietbi'
#     name = fields.Char(required=True)
#     brand_id = fields.Many2one('tonkho.brand',ondelete="restrict",string=u'Hãng sản xuất')
#     categ_id = fields.Many2one(
#         'product.category', u'Nhóm',ondelete="restrict")
# class Brand(models.Model):
#     _name = 'tonkho.brand'
#     name = fields.Char(required=True)
   

class ProductTemplate(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = 'product.template'
    type = fields.Selection(selection_add=[],default = 'product')
    thiet_bi_id = fields.Many2one('tonkho.thietbi', string = u'Thiết bị',ondelete="restrict")
    brand_id = fields.Many2one('tonkho.brand',string=u'Hãng sản xuất')
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    quant_ids = fields.One2many('stock.quant', 'product_id',domain=[('location_id.usage','=','internal')],string=u'Trong kho')#domain=[('location_id.usage','=','internal')]
    stock_location_id_selection = fields.Selection('get_stock_for_selection_field_', store=False)
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
#         ('lot', 'By Lots'),
        ('none', 'No Tracking')],required=True,string=u'Có SN hay không',default='serial')
    
    is_co_sn_khong_tinh_barcode = fields.Boolean(string=u'Is có SN không tính Barcode')
    tram_ltk_tao = fields.Boolean()
    dang_chay_tao = fields.Boolean()
    du_phong_tao = fields.Boolean()
    tram_tti_tao = fields.Boolean()
    thiet_bi_id_tti = fields.Many2one('tonkho.thietbi', string = u'Thiết bị TTI')
    thiet_bi_id_ltk = fields.Many2one('tonkho.thietbi', string = u'Thiết bị LTK')
    brand_id_tti = fields.Many2one('tonkho.brand',string=u'Hãng sản xuất TTI')
    name_khong_dau = fields.Char(compute='name_khong_dau_',store=True)
    name_viet_tat = fields.Char(compute='name_khong_dau_',store=True)
    @api.depends('name')
    def name_khong_dau_(self):
        name_khong_dau_compute(self)
#         for r in self:
#             if r.name:
#                 r.name_khong_dau = unidecode(r.name)
#     
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
  
        recs = self.search(['|',('name', operator, name), ('name_khong_dau', operator, name)],args, limit=limit)
        return recs.name_get()
    
    
    def get_stock_for_selection_field_(self):
        locs = self.env['stock.location'].search([('is_kho_cha','=',True)])
        rs = list(map(lambda i:(i.name,i.name),locs))
        return rs
    def write(self, vals):
        return super(ProductTemplate, self.with_context(search_move_line_in_write=1)).write(vals) # vi sao phai lam vay --> de change uom cua PT
    

        