# -*- coding: utf-8 -*-
from odoo import models, fields, api#,tools
from odoo.exceptions import UserError#, except_orm
# import itertools
# from odoo.addons.product.models.product_template import  ProductTemplate
# from unidecode import unidecode
from odoo.addons.dai_tgg.mytools import name_khong_dau_compute


class PN(models.Model):
    _name = 'tonkho.pn'
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name, product_id)', 'The combination of pn and product must be unique !'),
    ]
    name = fields.Char(required=True)
    product_id = fields.Many2one('product.product',required=True,ondelete='cascade')
    sn_ids = fields.One2many('stock.production.lot','pn_id',string='Serial numbers')
    running_or_prepare = fields.Selection([('running',u'Đang chạy'),('prepare',u'Dự phòng')])
#     import_location_id = fields.Many2one('stock.location')
    tram_ltk_tao = fields.Boolean()
    dang_chay_tao = fields.Boolean()
    du_phong_tao = fields.Boolean()
    context = fields.Char(compute='context_')
    @api.depends('name')
    def context_(self):
        self.context = self._context
# class PNCon(models.Model):
#     _name = 'tonkho.pncon'
#     _inherits = {'tonkho.pn': 'pn_id'}
#     name2 = fields.Char()
class Categ(models.Model):
    _inherit = 'product.category'
    stt_for_report = fields.Integer(u'STT cho báo cáo ngày')
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
    
    
class ThietBi(models.Model):
    _name = 'tonkho.thietbi'
    name = fields.Char(required=True)
    brand_id = fields.Many2one('tonkho.brand',ondelete="restrict",string=u'Hãng sản xuất')
    categ_id = fields.Many2one(
        'product.category', u'Nhóm',ondelete="restrict")
class Brand(models.Model):
    _name = 'tonkho.brand'
    name = fields.Char(required=True)
   