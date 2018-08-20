# -*- coding: utf-8 -*-
from odoo import models, fields, api#,tools
from odoo.exceptions import UserError#, except_orm
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
import psycopg2
# import itertools
# from odoo.addons.product.models.product_template import  ProductTemplate

class PN(models.Model):
    _name = 'tonkho.pn'
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name, product_id)', 'The combination of pn and product must be unique !'),
    ]
    name = fields.Char()
    product_id = fields.Many2one('product.product')
    sn_ids = fields.One2many('stock.production.lot','pn_id')
    running_or_prepare = fields.Selection([('running',u'Đang chạy'),('prepare',u'Dự phòng')])
    import_location_id = fields.Many2one('stock.location')
    tram_ltk_tao = fields.Boolean()
    dang_chay_tao = fields.Boolean()
    du_phong_tao = fields.Boolean()
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
        ('none', 'No Tracking')],default='none', required=True,string=u'Có SN hay không')
    
    is_co_sn_khong_tinh_barcode = fields.Boolean()
    pn_id = fields.Many2one('tonkho.pn')
    tram_ltk_tao = fields.Boolean()
    dang_chay_tao = fields.Boolean()
    du_phong_tao = fields.Boolean()
    tram_tti_tao = fields.Boolean()
    thiet_bi_id_tti = fields.Many2one('tonkho.thietbi', string = u'Thiết bị TTI')
    brand_id_tti = fields.Many2one('tonkho.brand',string=u'Hãng sản xuất TTI')
    
#     is_co_sn_thuan_pr = fields.Boolean(related='product_variant_id.is_co_sn_thuan_pr',store=True)
    def get_stock_for_selection_field_(self):
        locs = self.env['stock.location'].search([('is_kho_cha','=',True)])
        rs = list(map(lambda i:(i.name,i.name),locs))
        return rs
    def write(self, vals):
        return super(PT, self.with_context(search_move_line_in_write=1)).write(vals) # vi sao phai lam vay --> de change uom cua PT
    
#     @api.model
#     def create(self, vals):
#         ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
#         # TDE FIXME: context brol
# #         tools.image_resize_images(vals)
#         template = super(ProductTemplate, self).create(vals)
#         print ("template.product_variant_ids 1",template.product_variant_ids)
#         template.with_context(create_from_tmpl=True).create_variant_ids()
#         print ("template.product_variant_ids 2",template.product_variant_ids)
#         raise ValueError('stop..')
#         return template

#     @api.model
#     def create(self, vals):
#         ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
#         # TDE FIXME: context brol
# #         tools.image_resize_images(vals)
#         template = super(PT, self).create(vals)
#         print ('self._context',self._context)
#         if "create_product_product" not in self._context:
#             print ('**ok')
#             template.with_context(create_from_tmpl=True).create_variant_ids()
# 
#         # This is needed to set given values to first variant after creation
#         related_vals = {}
#         if vals.get('barcode'):
#             related_vals['barcode'] = vals['barcode']
#         if vals.get('default_code'):
#             related_vals['default_code'] = vals['default_code']
#         if vals.get('standard_price'):
#             related_vals['standard_price'] = vals['standard_price']
#         if vals.get('volume'):
#             related_vals['volume'] = vals['volume']
#         if vals.get('weight'):
#             related_vals['weight'] = vals['weight']
#         if related_vals:
#             template.write(related_vals)
#         return template
# 
#     @api.multi
#     def create_variant_ids(self):
#         print ('self.product_variant_ids',self.product_variant_ids)
#         Product = self.env["product.product"]
#         AttributeValues = self.env['product.attribute.value']
#         for tmpl_id in self.with_context(active_test=False):
#             # adding an attribute with only one value should not recreate product
#             # write this attribute on every product to make sure we don't lose them
#             variant_alone = tmpl_id.attribute_line_ids.filtered(lambda line: len(line.value_ids) == 1).mapped('value_ids')
#             print ('**variant_alone',variant_alone)
#             for value_id in variant_alone:
#                 updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
#                 updated_products.write({'attribute_value_ids': [(4, value_id.id)]})
#             print ('***self.product_variant_ids 1',self.product_variant_ids)
#             # iterator of n-uple of product.attribute.value *ids*
#             variant_matrix = [
#                 AttributeValues.browse(value_ids)
#                 for value_ids in itertools.product(*(line.value_ids.ids for line in tmpl_id.attribute_line_ids if line.value_ids[:1].attribute_id.create_variant))
#             ]
#             print ('**variant_matrix',variant_matrix)
#             # get the value (id) sets of existing variants
#             existing_variants = {frozenset(variant.attribute_value_ids.ids) for variant in tmpl_id.product_variant_ids}
#             # -> for each value set, create a recordset of values to create a
#             #    variant for if the value set isn't already a variant
#             print ('**existing_variants',existing_variants)
#             print ('***self.product_variant_ids 2',self.product_variant_ids)
# 
#             to_create_variants = [
#                 value_ids
#                 for value_ids in variant_matrix
#                 if set(value_ids.ids) not in existing_variants
#             ]
#             print ('to_create_variants**',to_create_variants)
#             # check product
#             variants_to_activate = self.env['product.product']
#             variants_to_unlink = self.env['product.product']
#             print ('**tmpl_id.product_variant_ids',tmpl_id.product_variant_ids)
#             print ('***self.product_variant_ids 3',self.product_variant_ids)
#             
#             
#             for product_id in tmpl_id.product_variant_ids:
#                 if not product_id.active and product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant) in variant_matrix:
#                     variants_to_activate |= product_id
#                 elif product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant) not in variant_matrix:
#                     variants_to_unlink |= product_id
#             print ('***self.product_variant_ids 4',self.product_variant_ids)
#             if variants_to_activate:
#                 variants_to_activate.write({'active': True})
#             # create new product
#             print ('***self.product_variant_ids 5',self.product_variant_ids)
#            
#             print ('**to_create_variants',to_create_variants)
#             for variant_ids in to_create_variants:
#                 print ('**variant_ids.ids',variant_ids.ids)
#                 new_variant = Product.create({
#                     'product_tmpl_id': tmpl_id.id,
#                     'attribute_value_ids': [(6, 0, variant_ids.ids)]
#                 })
#             # unlink or inactive product
#             print ('***self.product_variant_ids 6',self.product_variant_ids)
#             for variant in variants_to_unlink:
#                 try:
#                     with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
#                         variant.unlink()
#                 # We catch all kind of exception to be sure that the operation doesn't fail.
#                 except (psycopg2.Error, except_orm):
#                     variant.write({'active': False})
#                     pass
# #             raise ValueError('stop..')
#         print ('self.product_variant_ids',self.product_variant_ids)
#         return True       
        