# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.addons.tonkho.tonkho_tool import get_or_create_object_sosanh

# thừa bên dai_tgg có rồi cũng giống như totrinh
class User(models.Model):
    _inherit = 'res.users'
    department_id = fields.Many2one('hr.department')
    
    
    
class Department(models.Model):
    _inherit = 'hr.department'
    sequence_id = fields.Many2one('ir.sequence',compute='sequence_id_',store=True)
#     default_stock_location_id =fields.Many2one('stock.location',compute='location_id_',store=True)
    default_stock_location_id =fields.Many2one('stock.location')
    
    
    @api.depends('name')
    def sequence_id_(self):
        for r in self:
            if r.name:
                if not r.sequence_id:
                    sequence_id = get_or_create_object_sosanh(self, 'ir.sequence', {'name':r.name},
                                    )
                    r.sequence_id = sequence_id.id
                else:
                    r.sequence_id.name = r.name
               
                    
                    
                    
#     @api.depends('name')
#     def location_id_(self):
#         for r in self:
#             if r.name:
# #                 if not r.sequence_id:
# #                     sequence_id = get_or_create_object_sosanh(self, 'ir.sequence', {'name':r.name},
# #                                     )
# #                     r.sequence_id = sequence_id.id
# #                 else:
# #                     r.sequence_id.name = r.name
#                 if not r.default_stock_location_id:
#                     default_stock_location_id = get_or_create_object_sosanh(self, 'stock.location', {'name': r.name + u' Dự Phòng'},
#                                     )
#                     r.default_stock_location_id = default_stock_location_id.id
#                 else:
#                     r.default_stock_location_id.name = r.name + u' Dự Phòng'
                    
                    
    def get_department_name_for_report_(self):
        for r in self:
            names = []
            if r.cong_ty_type.name:
                names.append(r.cong_ty_type.name)
            names.append(r.name)
            return  u' '.join(names)