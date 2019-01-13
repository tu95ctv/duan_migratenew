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
    
    # field ghi đè
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
#         ('lot', 'By Lots'),
        ('none', 'No Tracking')],required=True,
                                compute='tracking_',
                                store=True,
                                string=u'Có SN hay không',
                                default='none'
                                )
    
    @api.depends('sn_ids')
    def tracking_(self):
        print ('in tracking_')
        for r in self:
            rs = self.env['stock.production.lot'].search([('product_id','=',r.id)], limit=1)
            r.tracking = 'serial' if rs else 'none'
            
            
    # field mới
    lot_ids = fields.One2many('stock.production.lot','product_id')
    pn = fields.Char(string='Part number')
    pn_replace = fields.Char(compute='pn_replace_',store=True)
    @api.depends('name')
    def pn_replace_(self):
        for r in self:
            if r.pn:
                r.pn_replace = pn_replace(r.pn)
    sn_ids = fields.One2many('stock.production.lot','product_id',string='Serial numbers')
   

    @api.multi
    def name_get(self):
        result = []
        if self._context.get('show_pn_in_lot_id_name_get'):
            for r in self:
                    result.append((r.id, "%s%s" % (r.name,r.pn and  u' (%s)'%r.pn or '')))
        else:
            result = super(Product, self).name_get()
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
        return recs.name_get()
    def _get_domain_locations(self):
        default_location_name = self.env.user.department_id.default_location_id.name
        if default_location_name:
            return super(Product,self.with_context(location=default_location_name))._get_domain_locations()
        else:
                raise UserError (u'default_location_name Không Có')
            
            
