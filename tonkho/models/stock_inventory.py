# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class Inventory(models.Model):
    _inherit = "stock.inventory"
    #over write origin
    @api.model
    def _default_location_id_d4_write(self):
        default_location_id = self.env.user.department_id.default_location_id
        if default_location_id:
            return default_location_id.id
        else:
            raise UserError(_('You must define a default_location_id of department_id.') )
    location_id = fields.Many2one(
        'stock.location', 'Inventoried Location',
        readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        default=_default_location_id_d4_write)
    
    
    
    
    
    