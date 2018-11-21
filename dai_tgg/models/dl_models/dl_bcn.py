# -*- coding: utf-8 -*-
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from openerp.http import request
import xlwt
from odoo import fields
from odoo.exceptions import UserError
from copy import deepcopy
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str
from collections import  OrderedDict
from odoo.addons.dai_tgg.mytools import  Convert_date_orm_to_str
from collections import  OrderedDict
from odoo.addons.downloadwizard.models.dl_models.dl_model import  write_all_row
from odoo.addons.downloadwizard.models.dl_models.dl_model import  get_width
from odoo.addons.downloadwizard.models.dl_models.dl_model import  stt_
from odoo.addons.downloadwizard.models.dl_models.dl_model import  generate_easyxf
from odoo.addons.downloadwizard.models.dl_models.dl_model import  bold_style,bold_style_italic,normal_style,bbbg_normal_style,center_nomal_style
# def get_width(num_characters):
#     return int((1+num_characters) * 256)

# def stt_(v,needdata): 
#     v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
#     return v  



FIELDNAME_FIELDATTR_thuebao = [
          ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('msc',{}),
          ('date',{'func': lambda v,n: Convert_date_orm_to_str(v) }),
          ('tb_cap_nhat',{}),
          ('tb_mo_may',{}),
          ('tb_tat_may',{}),
          ('tai_cp',{}),
                    ]
Export_Para_thuebao = {
    'exported_model':'dai_tgg.thuebaoline',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_thuebao,
#     'gen_domain':gen_domain_stock_quant,
#     'search_para':{'order': 'loai_record asc'},#desc
    }
##################
def gen_domain_cvi(dl_obj):
    domain = []
    if dl_obj.date:
        domain.append(('ngay_bat_dau','>=',dl_obj.date))
    if dl_obj.end_date:
        domain.append(('ngay_bat_dau','<=',dl_obj.end_date))
        
    return domain

FIELDNAME_FIELDATTR_cvi =OrderedDict( [
          ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('department_id',{}),
          ('loai_record',{}),
          ('categ_id',{}),
          ('thiet_bi_id',{}),
          ('tvcv_id',{'string': lambda needdata_from_table: u'Loại sự cố' if  needdata_from_table['loai_record'] == u'Sự Cố' else u'Loại CV/Sự vụ'}),
          ('noi_dung',{}),
          ('nguyen_nhan',{ 'string':u'Nguyên nhân','skip_field':lambda needdata_from_table:  needdata_from_table['loai_record'] != u'Sự Cố'}),
          ('gio_bat_dau',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
          ('gio_ket_thuc',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
                    ])
Export_Para_cvi = {
    'exported_model':'cvi',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_cvi,
    'gen_domain':gen_domain_cvi,
    'search_para':{'order': 'loai_record asc'},#desc
    }

def dl_cvi(dl_obj,append_domain = []):
    Export_Para_cvi_copy = deepcopy(Export_Para_cvi)
    Export_Para_cvi_copy['FIELDNAME_FIELDATTR']['nguyen_nhan']['skip_field'] = False
    Export_Para_cvi_copy['FIELDNAME_FIELDATTR']['tvcv_id']['string'] = u'Loại'
    filename = 'cvi'
    name = "%s%s" % (filename, '.xls')
    wb =  download_model(dl_obj,
                         Export_Para=Export_Para_cvi_copy,
                         append_domain=append_domain
                        )
    return wb,name


def  write_before_title (kargs):
    worksheet = kargs['worksheet']
    row_index_before_title = kargs['row_index_before_title']
    col_index_before_title = kargs['col_index_before_title']
    noi_dung = kargs['noi_dung']
    style = kargs.get('style',normal_style)
    worksheet.write(row_index_before_title, col_index_before_title, noi_dung,style)
    
    
LOAI_REC_=OrderedDict([(u'Sự Cố',{'noi_dung':u'A. TÌNH HÌNH HƯ HỎNG, SỰ CỐ TRÊN MẠNG:'}),
           (u'Công Việc',{'noi_dung':u'B. TÌNH HÌNH THAY ĐỔI THIẾT BỊ VÀ DỊCH VỤ MẠNG:'})
           ])



def thuebaotable_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
#     worksheet.write(row_index, 0, u'C. TÌNH HÌNH THUÊ BAO CẬP NHẬT MẠNG DI ĐỘNG (lúc 19h00):',header_bold_style)
    append_domain = [('date','=',dl_obj.date)]
    n_row = download_model(dl_obj,
             Export_Para=Export_Para_thuebao,
            append_domain=append_domain,
#              workbook=None,
             worksheet=worksheet,
             ROW_TITLE = row_index,
             return_more_thing_for_bcn = True,
             no_gray = True,
             is_set_width = False
                             )
    return n_row 
                             
                             

def table_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
#     cates = kargs ['cates'] 
    Export_Para_cvi_copy1 = deepcopy(Export_Para_cvi)
    is_show_loai_record = dl_obj.env['ir.config_parameter'].sudo().get_param('dai_tgg.' + 'is_show_loai_record')
    Export_Para_cvi_copy1['FIELDNAME_FIELDATTR']['loai_record']['skip_field'] = not is_show_loai_record
    
    cates = request.env['product.category'].search([('stt_for_report','!=',False)],order='stt_for_report asc')
    row_index_begin = row_index
    needdata_from_table = {}
    for loai_record,attrs in LOAI_REC_.items():
            needdata_from_table ['loai_record'] = loai_record
            noi_dung_1= attrs['noi_dung']
            row_index +=1
            write_before_title(
                {'worksheet' :worksheet,
                'row_index_before_title' :row_index,
                'col_index_before_title' :0,
                'noi_dung':noi_dung_1,
                'style':bold_style}
                ) # ghi A. sự cố , B. công việc
            row_index +=2
            if loai_record ==u'Công Việc':
                domain_loai_record = [('loai_record','in',[u'Công Việc',u'Sự Vụ'])]
            else:
                domain_loai_record = [('loai_record','=',loai_record)]
            for cate in cates:# categ_id # ghi các đầu nhóm 1. IP , 2TRD
#                 row_index +=1
                Export_Para_cvi_copy = deepcopy(Export_Para_cvi_copy1)
                domain =[('categ_id','=',cate.id),(('is_bc','=',True))] + domain_loai_record
               
#                 kargs_write_before_title = {'worksheet' :worksheet,
#                                                             'row_index_before_title' :row_index ,
#                                                             'col_index_before_title' :0,
#                                                             'noi_dung':u'%s/ %s'%(cate.stt_for_report,cate.name),
#                                                             'style':bold_style_italic}
#                 write_before_title(kargs_write_before_title)    
#                 row_index +=1
                
                n_row = download_model(dl_obj,
                             Export_Para=Export_Para_cvi_copy,
                             append_domain=domain,
                             workbook=None,
                             worksheet=worksheet,
                             ROW_TITLE = row_index ,
                             return_more_thing_for_bcn = True,
                            write_before_title = write_before_title,
                            
                            kargs_write_before_title = {'worksheet' :worksheet,
                                                                        'row_index_before_title' :row_index ,
                                                                        'col_index_before_title' :0,
                                                                        'noi_dung':u'%s/%s'%(cate.stt_for_report,cate.name),
                                                                        'style':bold_style_italic},
                             
                             needdata_from_table =needdata_from_table,
                             no_gray = True,
                             OFFSET_COLUMN = 0,
                             write_title_even_not_recs_for_title=True,
                             
                                                               
                             )
                row_index += n_row
    return row_index- row_index_begin + 1

def hom_nay_(ws,f_name,fixups,needdata,row,dl_obj):
    return u'Ngày ' + Convert_date_orm_to_str(dl_obj.date,format_date = '%d/%m/%Y') 



def dl_bcn(dl_obj,append_domain = []):
    filename = u'Báo cáo ngày_%s' %fields.Date.from_string(dl_obj.date).strftime('%d_%m_%Y')
    name = "%s%s" % (filename, '.xls')
    fixups =[  
                 ('trung_tam1',{'range':[0,0,0,3],'val':u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=11, vert = 'center',horiz = 'center'))}),
                 ('trung_tam2',{'range':[1,1,0,3],'val':u'ĐÀI VIỄN THÔNG HCM', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('chxhcnvn',{'range':[0,0,4,7],'val':u'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('dltdhp',{'range':[1,1,4,7],'val':u'Độc lập - Tự do - Hạnh Phúc', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
#                     ('so',{'range':[2,2,0,2],'val':u'Số: %s/%s-%s'%(dl_obj.stt_trong_bien_ban_in,dl_obj.ban_giao_or_nghiem_thu,dl_obj.department_id.short_name), 'style':xlwt.easyxf(generate_easyxf(height=12, vert = 'center',horiz = 'center'))}),
#                     ('bbg',{'range':[3,3,0,7],'val':u'BIÊN BẢN BÀN GIAO VẬT TƯ', 'style':bbbg_normal_style,'height':1119,'off_set':1}),
                 ('bbg',{'range':[3,3,0,7],'val':u'BÁO CÁO THÔNG TIN', 'style':bbbg_normal_style,'height':1119,'off_set':1}),
                 ('hom_nay',{'range':[4,4,0,7],'val':None, 'val_func': hom_nay_,'style':center_nomal_style }),
                 ('table',{'range':['auto', 0],'val':None,'func':table_ ,'offset':3 }),
                 ('thuebao_title',{'range':['auto', 0],'val':None,'val':u'C. TÌNH HÌNH THUÊ BAO CẬP NHẬT MẠNG DI ĐỘNG (lúc 19h00):','style':bold_style,'offset':1 }),
                 ('thuebaotable',{'range':['auto', 0],'val':None,'func':thuebaotable_ ,'offset':2}),
                 ('pho_dai_vthcm',{'range':['auto', 1],'val':u'Phó đài VT HCM',}),
                 ('tphcm',{'range':['auto', 7],'offset':0, 'val':u'Tp. Hồ Chí Minh, Ngày %s'%Convert_date_orm_to_str(dl_obj.date),}),
                 ('ten_pho_dai_vthcm',{'range':['auto', 1],'offset':5,'val':u'Nguyễn Văn Xuân',}),
                 ('ten_nguoi_bc',{'range':['auto', 7],'offset':0,'val':dl_obj.env.user.name,}),
                 ]
    wb = write_all_row(fixups,dl_obj,None)
        
    return wb,name
        
    


