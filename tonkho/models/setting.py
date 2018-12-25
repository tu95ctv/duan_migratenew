# -*- coding: utf-8 -*-
from odoo import models, fields, api
class SomeThing(models.Model):
    _name='tonkho.something'
    name = fields.Char()
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    cancel_mode = fields.Boolean()
    is_validate_mode  = fields.Boolean()
    is_bg_or_nt_tra_do_muon = fields.Boolean()
    is_show_for_admin_tram_nao_tao_vat_tu = fields.Boolean()
    not_allow_check_lot_id_in_different_location =  fields.Boolean()
    
    group_show_thong_tin_khong_dau = fields.Selection([
        (0, u'Không show thông tin name không dấu'),
        (1, u'Show thông tin name không dấu')
        ], u"Show thông tin name không dấu", implied_group='tonkho.show_thong_tin_khong_dau')
    
    

#     font_height = fields.Integer()
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        for  f_name in ('cancel_mode','is_validate_mode','is_bg_or_nt_tra_do_muon','is_show_for_admin_tram_nao_tao_vat_tu','not_allow_check_lot_id_in_different_location'):
            res[ f_name] = self.env['ir.config_parameter'].sudo().get_param('tonkho.' + f_name)
            
        return res
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for f_name in ('cancel_mode','is_validate_mode','is_bg_or_nt_tra_do_muon','is_show_for_admin_tram_nao_tao_vat_tu','not_allow_check_lot_id_in_different_location'):
                self.env['ir.config_parameter'].sudo().set_param('tonkho.'+f_name, getattr(self, f_name))
    #         self.env['ir.config_parameter'].sudo().set_param('tonkho.cancel_mode', self.cancel_mode)
#         self.env['ir.config_parameter'].sudo().set_param('tonkho.is_validate_mode', self.is_validate_mode)