# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from lxml import etree
from urllib.parse import quote
import base64
import contextlib
import io
# from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
# from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
# from odoo.addons.dai_tgg.models.dl_models.dl_tvcv import  download_tvcv1
# from odoo.addons.dai_tgg.models.dl_models.dl_user import  download_user

class DownloadQuants(models.TransientModel):
    _name = "downloadwizard.download"
    name = fields.Char()
    parent_location_id =  fields.Many2one('stock.location', 
#                                           default=lambda self:self.env.user.department_id.default_location_id.id, string=u'Kho cha dự phòng'
                                          )
    parent_location_runing_id =  fields.Many2one('stock.location',
#                                                  default=lambda self:self.env.user.department_id.default_location_running_id.id,
                                                 string=u'Kho cha đang chạy'
                                                 )
#     test =  fields.Text()
    data = fields.Binary('File', readonly=True)
    is_moi_sheet_moi_loai = fields.Boolean(string=u' Chia nhóm vật tư')
    is_not_skip_field_stt = fields.Boolean(groups="base.group_erp_manager")
#     is_dl_right_now = fields.Boolean(string=u'Download ngay(phải cho phép pop up)')
#     domain_text = fields.Text(default = lambda self: self._context)
    
#         return datetime.datetime.now()
#     ngay_bat_dau_filter = fields.Datetime(string=u'Ngày Bắt Đầu',default= lambda self: self.ngay_bat_dau_filter_())
#     ngay_ket_thuc_filter = fields.Datetime(string=u'Ngày Kết Thúc',default=lambda self: self.ngay_ket_thuc_filter_())
#     
#     def ngay_ket_thuc_filter_(self): # before , lay can tren
#         dm  = self._context.get('active_domain',None)
#         print ('active_domain in  ngay_ket_thuc_filter_ default',dm)
#         if dm:
#             for i in dm:
#                 if len(i)==3:
#                     x,y,z = i
#                     if x == 'create_date' and y == '<=':
#                         return z
#     
#     def ngay_bat_dau_filter_(self):#after , lay can duoi
#         dm  = self._context.get('active_domain',None)
#         print ('active_domain in ngay_bat_dau_filter_ ',dm)
#         if dm:
#             for i in dm:
#                 if len(i) ==3:
#                     x,y,z = i
#                     if x == 'create_date' and y == '>=':
#                         return z
    
   
    
    def model_name_(self):
        active_model =  self._context.get('transfer_active_model') or self._context.get('active_model')
        return active_model

    model_name = fields.Char(default=model_name_)
    
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(DownloadQuants, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         doc = etree.XML(res['arch'])
#         if view_type =='form':
#             nodes =  doc.xpath("//button[@name='download_all_model']")
#             if len(nodes):
#                 node = nodes[0]
#                 active_model = self._context['active_model']
#                 try:
#                     active_model = active_model.split('.')[1]
#                 except:
#                     active_model = active_model.split('.')[0]
#                 translate_dict_for_model = {'quant':u'Số lượng trong kho','product':u'Vật tư'}
#                 node.set('string', "Download %s"%translate_dict_for_model.get(active_model,active_model))
#         res['arch'] = etree.tostring(doc, encoding='unicode')
#         return res
    
    

    @api.multi
    def gen_pick_func(self): 
        return {}
    @api.multi
    def download_all_model(self):
        active_domain = self._context['active_domain']
        self.domain_text = self._context
        model =self._context.get('transfer_active_model') or self._context['active_model']
        
#         pick_func = {'stock.quant':download_quants,'product.product':download_product,'tvcv':download_tvcv1,'res.users':download_user}
#         pick_func = {'tvcv':download_tvcv1,'res.users':download_user}
        pick_func = self.gen_pick_func()
        if not model:
            raise UserError('sao khong co model nao map, model:%s'%model)
        download_right_now = self._context.get('download_right_now')
        if download_right_now:#self.is_dl_right_now:
#             url = '/web/binary/download_model?model=%s&id=%s&active_domain=%s'%(model, self.id,quote(u'%s'%active_domain))
            download_from_model = self._context.get('download_from_model') or ''
#             active_domain = ''
            url = '/web/binary/download_model/%s?model=%s&id=%s&active_domain=%s'%(download_from_model,model, self.id,quote(u'%s'%active_domain))
            print ('url',url)
            return {
                 'type' : 'ir.actions.act_url',
                 'url': url,
                 'target': 'new',
            }
        else:
            
            dl_obj = self
            call_func = pick_func[model]
            workbook,name = call_func(dl_obj,active_domain)
            
            with contextlib.closing(io.BytesIO()) as buf:
                workbook.save(buf)
                out = base64.encodestring(buf.getvalue())
            dl_obj.write({ 'data': out, 'name': name})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'downloadwizard.download',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': dl_obj.id,
                'context':{'active_model':model},
                'views': [(False, 'form')],
                'target': 'new',
            }
#     @api.multi
#     def test1(self):
#         sql_multi_2 = '''select * from stock_quant'''
#         self.env.cr.execute(sql_multi_2)
#         result_2 = self.env.cr.dictfetchall()
#         self.test = result_2
#         print ('self._context',self._context)
#         raise UserError('akakak')

