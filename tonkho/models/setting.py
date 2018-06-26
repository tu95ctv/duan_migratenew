# -*- coding: utf-8 -*-
from odoo import models, fields, api
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    cancel_mode = fields.Boolean()
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            cancel_mode=self.env['ir.config_parameter'].sudo().get_param('tonkho.cancel_mode')
        )
        return res
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('tonkho.cancel_mode', self.cancel_mode)
        
        