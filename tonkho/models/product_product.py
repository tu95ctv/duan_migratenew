# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from lxml import etree
import os,inspect,sys
import datetime
from odoo.osv.orm import setup_modifiers

class Product(models.Model):
    _inherit = "product.product"
    
    lot_ids = fields.One2many('stock.production.lot','product_id')
    pn_ids = fields.One2many('tonkho.pn','product_id')
    len_pn = fields.Integer(compute='len_pn_',store=True,string=u'Số lượng PN')
    ghi_chu_cate = fields.Text()
    @api.depends('pn_ids')
    def len_pn_(self):
        for r in self:
            r.len_pn = len(r.pn_ids)
    def _get_domain_locations(self):
        default_location_name = self.env.user.department_id.default_location_id.name
        if default_location_name:
            return super(Product,self.with_context(location=default_location_name))._get_domain_locations()
        else:
                raise UserError (u'default_location_name Không Có')
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Product, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type =='tree':
#             currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#             parent_path = os.path.abspath(os.path.join(currentdir, os.pardir))
#             test_path = os.path.join(parent_path, "test.txt")
#             with open(test_path, 'w') as the_file:
#                 the_file.write('%s'%res)
                
            is_show_for_admin_tram_nao_tao_vat_tu =   self.env['ir.config_parameter'].sudo().get_param('tonkho.' + 'is_show_for_admin_tram_nao_tao_vat_tu')
            doc = etree.fromstring(res['arch'])
            if not is_show_for_admin_tram_nao_tao_vat_tu:
                node =  doc.xpath("//field[@name='tram_ltk_tao']")[0]
                doc.remove(node)
                node =  doc.xpath("//field[@name='dang_chay_tao']")[0]
                doc.remove(node)
                node =  doc.xpath("//field[@name='du_phong_tao']")[0]
                doc.remove(node)
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res