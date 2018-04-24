from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
class StockLocation(models.Model):
    _inherit = 'stock.location'
    department_id =  fields.Many2one('hr.department')
    partner_id =  fields.Many2one('res.partner')
    def name_get(self):
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            while location.location_id and location.usage != 'view':
                location = location.location_id
#                 if not name:
#                     raise UserError(_('You have to set a name for this location.'))
                name = str(location.name) + "/" + str(name)
            ret_list.append((orig_location.id, name))
        return ret_list