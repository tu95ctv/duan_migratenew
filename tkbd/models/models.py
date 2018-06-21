# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Team(models.Model):
    _name = 'tkbd.team'
    name = fields.Char()
def chuyen_doi_ti_le_sang_2_so_float(ti_le):
    ti_les = ti_le.split(':')
    ti_les = map(chuyen_doi_hon_so_ra_so_float,ti_les)
    return ti_les
def chuyen_doi_hon_so_ra_so_float(val):
    vals = val.split(' ')
    vals = sum(map(chuyen_so_thap_phan_ra_so_float,vals))
    return vals
def chuyen_so_thap_phan_ra_so_float(val):
    vals = val.split('/')
    if len(vals) ==1:
        val = float(vals[0])
    else:
        val =  float(vals[0])/float(vals[1])
    return val
 
class Match(models.Model):
    _name = 'tkbd.match'
    name = fields.Char()
    team_1 = fields.Many2one('tkbd.team')
    team_2 = fields.Many2one('tkbd.team')
    score_1 = fields.Integer()
    score_2 = fields.Integer()
    chu = fields.Float(digits=(6,2))
    khach = fields.Float(digits=(6,2))
    ti_le = fields.Char()
    ti_le_float_1 = fields.Float(digits=(6,2), compute='ti_le_float_1_',store=True)
    ti_le_float_2 = fields.Float(digits=(6,2),compute='ti_le_float_1_',store=True)
    
    @api.depends('ti_le')
    def ti_le_float_1_(self):
        for r in self:
            if r.ti_le:
                r.ti_le_float_1,r.ti_le_float_2= chuyen_doi_ti_le_sang_2_so_float(r.ti_le)
         
        
        
        
        