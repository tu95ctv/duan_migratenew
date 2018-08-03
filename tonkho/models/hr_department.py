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
    sequence_id = fields.Many2one('ir.sequence')
    default_location_id =fields.Many2one('stock.location',string=u'Kho mặc định')
    default_location_running_id =fields.Many2one('stock.location',string=u'Kho mặc định đang chạy')
    
    @api.model
    def create(self, vals):
        try:
            name =  vals['name']
        except KeyError:
            raise UserError(u'Tạo department thì phải có field name')
        sequence_id = get_or_create_object_sosanh(self, 'ir.sequence', {'name':name})
        vals['sequence_id'] = sequence_id.id
        return super(Department, self).create(vals)
    def get_department_name_for_report_(self):
        for r in self:
            if r.report_name:
                return r.report_name
            else:
                return r.name
