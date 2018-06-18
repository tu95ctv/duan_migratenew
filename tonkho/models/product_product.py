# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = "product.product"
    def _get_domain_locations(self):
        default_location_name = self.env.user.department_id.default_location_id.name
        if default_location_name:
            return super(Product,self.with_context(location=default_location_name))._get_domain_locations()
        else:
                raise UserError (u'default_location_name Không Có')
