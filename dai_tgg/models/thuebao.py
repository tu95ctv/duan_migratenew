# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
adict = {
'MSSE2D':1,
'MSSE2G':2,
'MSS2F':3,
'MSSE2E':4,
'MSSE2F':5,
'MSS2C':6,
'TSS2A':7,
'TSC2B':8,
'SGSN2B':9,
'SGSN2C':10,
}

aselect =  (list(map(lambda i:(i,i),sorted(adict, key=adict.__getitem__))))

class Thuebaoline(models.Model):
    _name = 'dai_tgg.thuebaoline'
    msc = fields.Selection(aselect)
    tb_cap_nhat =  fields.Integer(u'TB cập nhật')
    tb_mo_may =  fields.Integer(u'TB mở máy')
    tb_tat_may =  fields.Integer(u'TB tắt máy')
    tai_cp =  fields.Integer(u'Tải CP')
    date = fields.Date(compute='date_',store=True,readonly=False)
    @api.depends('thuebao_id.date')
    def date_(self):
        for r in self:
            if r.thuebao_id: # Nếu không có dòng này thì khi sửa vẫn có giá trị củ
                r.date = r.thuebao_id.date
    stt =  fields.Integer()
    thuebao_id = fields.Many2one('dai_tgg.thuebao')
    
class Thuebao(models.Model):
    _name = 'dai_tgg.thuebao'
    date = fields.Date()
    thuebaoline_ids =  fields.One2many('dai_tgg.thuebaoline','thuebao_id',copy=True)
    
