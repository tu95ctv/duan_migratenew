# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    
    
#     @api.multi
#     def name_get(self):
#         res = []
#         for r in self:
#             res.append((r.id,r.name +' ahihi'))
#         return res
#     
    
    