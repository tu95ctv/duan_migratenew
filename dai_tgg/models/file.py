# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
class File(models.Model):
    _name = 'dai_tgg.file'
    name = fields.Char(string=u'File name')
    file = fields.Binary( attachment=True)
    mo_ta = fields.Text(string=u'Mô tả file')