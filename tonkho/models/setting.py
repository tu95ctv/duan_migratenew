# -*- coding: utf-8 -*-
from odoo import models, fields, api
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    cancel_mode = fields.Boolean()
    is_validate_mode  = fields.Boolean()
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        for  f_name in ('cancel_mode','is_validate_mode'):
            res[ f_name] =self.env['ir.config_parameter'].sudo().get_param('tonkho.' + f_name)
            
        return res
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for f_name in ('cancel_mode','is_validate_mode'):
                self.env['ir.config_parameter'].sudo().set_param('tonkho.'+f_name, getattr(self, f_name))
    #         self.env['ir.config_parameter'].sudo().set_param('tonkho.cancel_mode', self.cancel_mode)
#         self.env['ir.config_parameter'].sudo().set_param('tonkho.is_validate_mode', self.is_validate_mode)