# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class Inventory(models.Model):
    _inherit = "stock.inventory"
    #over write origin
    def action_done(self):
        return super(Inventory, self.with_context(action_done_from_stock_inventory=True)).action_done()
    @api.model
    def _default_location_id_d4_write(self):
        default_location_id = self.env.user.department_id.default_location_id
        if default_location_id:
            return default_location_id.id
        else:
            raise UserError(_('You must define a default_location_id of department_id.') )
#     location_id = fields.Many2one(
#         'stock.location', 'Inventoried Location',
#         readonly=True, required=True,
#         states={'draft': [('readonly', False)]},
#         default=_default_location_id_d4_write)
    
    
    @api.model
    def default_get(self, fields):
        res = super(Inventory, self).default_get(fields)
        res['location_id'] = self._default_location_id_d4_write()
        return res
#         if 'barcode' in fields and 'barcode' not in res and res.get('complete_name'):
#             res['barcode'] = res['complete_name']
#         return res
    
    
    