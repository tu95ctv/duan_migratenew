# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.dai_tgg.models.dl_models.dl_tvcv import  download_tvcv1
from odoo.addons.dai_tgg.models.dl_models.dl_user import  download_user

from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_bcn
from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_cvi
class DownloadQuants(models.TransientModel):
    _inherit = "downloadwizard.download"
    date = fields.Date(default=fields.Date.context_today)
    @api.multi
    def gen_pick_func(self): 
        rs = super(DownloadQuants, self).gen_pick_func()
        pick_func = {'tvcv':download_tvcv1,'res.users':download_user,'download_bcn':dl_bcn,'cvi': dl_cvi}
        rs.update(pick_func)
        return rs