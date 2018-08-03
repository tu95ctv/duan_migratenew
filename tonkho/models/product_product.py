# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = "product.product"
    #comment ngày 26/06 đưa context vào hàm _get_domain_locations để tính on hand hoặc forecasted quantity ở kho nào
    
    lot_ids = fields.One2many('stock.production.lot','product_id')
    
#     is_co_sn_thuan_pr = fields.Boolean(compute='is_co_sn_thuan_pr_',store=True)# ton tai name cua sn no có gia trị không chwua barcode và không chưa fale
    
#     @api.depends('lot_ids')
#     def is_co_sn_thuan_pr_(self):
#         for r in self:
#             if isinstance(r.id, int):
#                 rs = self.env['stock.production.lot'].search([('product_id','=',r.id),('name','not ilike','barcode'),('name','!=',False),('name','not ilike','unknown')],limit=1)
#                 if rs:
#                     r.is_co_sn_thuan_pr = True
#                 else:
#                     r.is_co_sn_thuan_pr = False
    def _get_domain_locations(self):
        default_location_name = self.env.user.department_id.default_location_id.name
        if default_location_name:
            return super(Product,self.with_context(location=default_location_name))._get_domain_locations()
        else:
                raise UserError (u'default_location_name Không Có')
