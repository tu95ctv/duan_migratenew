# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
from odoo.addons.tonkho.models.xl_tranfer_bb import write_xl_bb
import datetime

from odoo.addons.dai_tgg.models.tao_instance_new import importthuvien
from odoo.addons.dai_tgg.models.model_dict import gen_model_dict
from odoo.addons.tonkho.models.check_file import check_imported_file_sml

class DownloadQuants(http.Controller):
    
    @http.route('/web/binary/download_quants',type='http', auth="public")
    def download_quants_by_new_window(self,model, id, **kw):
        model = 'tonkho.downloadquants'
        dlcv_obj = request.env[model].browse(int(id))
        workbook = download_quants(dlcv_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=stockquantsdl_name_%s-date_%s.xls;target=blank' %(dlcv_obj.name,datetime.datetime.now().strftime('%d_%m_%H_%M')))],
            )
        workbook.save(response.stream)
        return response
    
    @http.route('/web/binary/download_xl_bbbg',type='http', auth="public")
    def download_xl_bbbg_by_new_window(self,model, id, **kw):
        model = 'stock.picking'
        dlcv_obj = request.env[model].browse(int(id))
        workbook,name = write_xl_bb(dlcv_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
            )
        workbook.save(response.stream)
        return response
    
    @http.route('/web/binary/download_checked_import_sml_file',type='http', auth="public")
    def download_checked_import_sml_file(self,model, id, **kw):
        dlcv_obj = request.env[model].browse(int(id))
#         title_row_for_import = [dlcv_obj.title_row_for_import or 0]
#         md = gen_model_dict(title_row_for_import)
        
#         workbook = importthuvien(dlcv_obj,import_for_stock_tranfer = md,key=u'stock.inventory.line.tong.hop.ltk.dp.tti.dp',key_tram='sml',not_create=True)
        wb,name= check_imported_file_sml(dlcv_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s;target=blank'%name)],
            )
        wb.save(response.stream)
        return response
    
    
    
    
    