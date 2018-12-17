# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from lxml import etree
import os,inspect,sys
import datetime
from odoo.osv.orm import setup_modifiers
import re
from odoo.addons.dai_tgg.mytools import pn_replace
class Product(models.Model):
    
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name,pn)', 'The serial number must be unique !'),
    ]
    _inherit = "product.product"
    lot_ids = fields.One2many('stock.production.lot','product_id')
    pn = fields.Char(string='Part number')
    pn_replace = fields.Char(compute='pn_replace_',store=True)
    @api.depends('name')
    def pn_replace_(self):
        for r in self:
            if r.pn:
#                 r.pn_replace = re.sub('[-_ \s]','',r.pn)
                r.pn_replace = pn_replace(r.pn)
                
                
#     pn_ids = fields.One2many('tonkho.pn','product_id')
#     len_pn = fields.Integer(compute='len_pn_',store=True,string=u'Số lượng PN')
#     ghi_chu_cate = fields.Text()
#     @api.depends('pn_ids')
#     def len_pn_(self):
#         for r in self:
#             r.len_pn = len(r.pn_ids)

    @api.multi
    def name_get(self):
        result = []
        if self._context.get('show_pn_in_lot_id_name_get'):
            for r in self:
                    result.append((r.id, "%s%s" % (r.name,r.pn and  u' (%s)'%r.pn or '')))
        else:
            result = super(Product, self).name_get()
#             for r in self:
                
#                 result.append((r.id, "%s %s" % (r.name,r.pn and  u'|%s'%r.pn or '')))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        
        if name:
            pn_replace_str = pn_replace(name)
            domain = ['|',('name', operator, name),('pn_replace',operator,pn_replace_str)] 
        else:
            domain = []
        recs = self.search(domain + args, limit=limit)
#         if not recs:
#             recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
    
    
    def _get_domain_locations(self):
        default_location_name = self.env.user.department_id.default_location_id.name
        if default_location_name:
            return super(Product,self.with_context(location=default_location_name))._get_domain_locations()
        else:
                raise UserError (u'default_location_name Không Có')
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(Product, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type =='tree':
# #             currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# #             parent_path = os.path.abspath(os.path.join(currentdir, os.pardir))
# #             test_path = os.path.join(parent_path, "test.txt")
# #             with open(test_path, 'w') as the_file:
# #                 the_file.write('%s'%res)
#                 
#             is_show_for_admin_tram_nao_tao_vat_tu =   self.env['ir.config_parameter'].sudo().get_param('tonkho.' + 'is_show_for_admin_tram_nao_tao_vat_tu')
#             doc = etree.fromstring(res['arch'])
#             if not is_show_for_admin_tram_nao_tao_vat_tu:
#                 node =  doc.xpath("//field[@name='tram_ltk_tao']")[0]
#                 doc.remove(node)
#                 node =  doc.xpath("//field[@name='dang_chay_tao']")[0]
#                 doc.remove(node)
#                 node =  doc.xpath("//field[@name='du_phong_tao']")[0]
#                 doc.remove(node)
#             res['arch'] = etree.tostring(doc, encoding='unicode')
#         return res