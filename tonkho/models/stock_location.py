from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
class StockLocation(models.Model):
    _inherit = 'stock.location'
    department_id =  fields.Many2one('hr.department')
    partner_id =  fields.Many2one('res.partner')
