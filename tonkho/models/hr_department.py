# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
class Department(models.Model):
    _inherit = 'hr.department'
    sequence_id = fields.Many2one('ir.sequence')
    default_stock_location_id =fields.Many2one('stock.location')
    def get_department_name_for_report_(self):
        for r in self:
            names = []
            if r.cong_ty_type.name:
                names.append(r.cong_ty_type.name)
            names.append(r.name)
            return  u' '.join(names)