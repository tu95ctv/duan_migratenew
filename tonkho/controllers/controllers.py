# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
from odoo.addons.tonkho.models.dl_models.xl_tranfer_bb import write_xl_bb
import datetime

from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict import gen_model_dict
from odoo.addons.tonkho.models.check_file import check_imported_file_sml


from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
from unidecode  import unidecode
import json

class DownloadQuants(http.Controller):
    
    
    
    @http.route('/web/binary/download_model',type='http', auth="public")
    def download_all_model_controller(self,model, id, **kw):

        active_domain = kw['active_domain']
        active_domain = active_domain.replace("'",'"')
        active_domain = json.loads(active_domain)
        dj_obj = request.env['tonkho.downloadquants'].browse(int(id))
       
        pick_func = {'stock.quant':download_quants,'product.product':download_product}
        call_func = pick_func[model]
        workbook,name = call_func(dj_obj,active_domain)
       
        name = unidecode(name)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
            )
        workbook.save(response.stream)
        return response
    
    
    
    @http.route('/web/binary/download_xl_bbbg',type='http', auth="public")
    def download_xl_bbbg_by_new_window(self,model, id, **kw):
        
        model = 'stock.picking'
        dj_obj = request.env[model].browse(int(id))
        workbook,name = write_xl_bb(dj_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
            )
        workbook.save(response.stream)
        return response
    
    @http.route('/web/binary/download_checked_import_sml_file',type='http', auth="public")
    def download_checked_import_sml_file(self,model, id, **kw):
        dj_obj = request.env[model].browse(int(id))
        wb,name= check_imported_file_sml(dj_obj)
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s;target=blank'%name)],
            )
        wb.save(response.stream)
        return response
    
    
    
    
    