# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.dai_tgg.models.dl_models.dl_tvcv import  download_tvcv
from odoo.addons.dai_tgg.models.dl_models.dl_user import  download_user

from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_bcn
from odoo.addons.dai_tgg.models.dl_models.dl_bcn import  dl_cvi

from odoo.addons.dai_tgg.models.dl_models.dl_p3 import  dl_p3



class DownloadQuants(models.TransientModel):
    _inherit = "downloadwizard.download"
    date = fields.Date(default=fields.Date.context_today,string=u'Ngày bắt đầu')
    end_date = fields.Date(default=fields.Date.context_today,string=u'Ngày kết thúc')
    chon_thang = fields.Selection([(u'Tháng Trước',u'Tháng Trước'),(u'Tháng Này',u'Tháng Này')],string = u'Chọn tháng')
    department_id = fields.Many2one('hr.department',u'Đơn vị (Trạm)')
    chi_tiet_hay_danh_sach = fields.Selection([('chi_tiet',u'Chi tiết'),('danh_sach',u'Danh Sách')],u'File chi tiết hay danh sách')
    @api.multi
    def gen_pick_func(self): 
        rs = super(DownloadQuants, self).gen_pick_func()
        pick_func = {'tvcv':download_tvcv,'res.users':download_user,'download_bcn':dl_bcn,'cvi': dl_cvi,'download_p3':dl_p3}
        rs.update(pick_func)
        return rs
    @api.multi
    def gen_pick_model_name(self): 
        rs = super(DownloadQuants, self).gen_pick_model_name()
        rs.update({'stock.quant':u'Kho','product.product':u'Vật tư','download_bcn':u'Báo cáo ngày','download_p3':u'Download P3'})
        return rs
    
    