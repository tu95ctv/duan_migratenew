# -*- coding: utf-8 -*-
from odoo.addons.dai_tgg.models.tao_instance_new import importthuvien
from odoo.addons.dai_tgg.models.model_dict import gen_model_dict

def check_imported_file_sml(dlcv_obj):
    title_row_for_import = [dlcv_obj.title_row_for_import or 0]
    md = gen_model_dict(title_row_for_import)
    workbook = importthuvien(dlcv_obj,import_for_stock_tranfer = md,
                             key=u'stock.inventory.line.tong.hop.ltk.dp.tti.dp',
                             key_tram='sml',
                             not_create=True)
    filename = 'check_file_of_%s-%s'%(dlcv_obj.filename,dlcv_obj.id)
    name = "%s%s" % (filename, '.xls')
    return workbook,name
