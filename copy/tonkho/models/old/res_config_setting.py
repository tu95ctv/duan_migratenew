# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    group_stock_multi_locations = fields.Boolean('Storage Locations', implied_group='stock.group_stock_multi_locations',
        help="Store products in specific locations of your warehouse (e.g. bins, racks) and to track inventory accordingly.")
    group_stock_production_lot = fields.Boolean("Lots & Serial Numbers",
        implied_group='stock.group_production_lot',default=True)