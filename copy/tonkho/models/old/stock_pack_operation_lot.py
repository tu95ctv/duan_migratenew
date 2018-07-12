# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    ghi_chu = fields.Text(related='lot_id.ghi_chu')
    ghi_chu_for_create = fields.Text(string=u'Ghi chú Cho Tạo SN')
    pn = fields.Char(related='lot_id.pn', string=u'Part Number')
    pn_for_create = fields.Char(string=u'Part Number')