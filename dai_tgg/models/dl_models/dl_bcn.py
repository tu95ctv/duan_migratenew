# -*- coding: utf-8 -*-
from odoo.addons.downloadwizard.models.dl_models.dl_model import  download_model
from openerp.http import request
import xlwt
from odoo.exceptions import UserError
from copy import deepcopy
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str
from collections import  OrderedDict
from odoo.addons.dai_tgg.mytools import  Convert_date_orm_to_str
from collections import  OrderedDict

def get_width(num_characters):
    return int((1+num_characters) * 256)

def stt_(v,needdata): 
    v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
    return v  

header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240")
bold_style_italic = xlwt.easyxf("font: bold on, name Times New Roman, height 240,italic on;")

normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")

FIELDNAME_FIELDATTR_thuebao = [
          ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('msc',{}),
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

FIELDNAME_FIELDATTR_quants =OrderedDict( [
          ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
          ('department_id',{}),
          ('loai_record',{}),
          ('categ_id',{}),
          ('thiet_bi_id',{}),
          ('tvcv_id',{'string': lambda needdata_from_table: u'Loại sự cố' if  needdata_from_table['loai_record'] == u'Sự Cố' else u'Loại CV/Sự vụ'}),
          ('noi_dung',{}),
          ('nguyen_nhan',{ 'string':u'Lý do','skip_field':lambda needdata_from_table:  needdata_from_table['loai_record'] != u'Sự Cố'}),
          ('gio_bat_dau',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
          ('gio_ket_thuc',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
                    ])
Export_Para_quants = {
    'exported_model':'cvi',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_quants,
#     'gen_domain':gen_domain_stock_quant,
    'search_para':{'order': 'loai_record asc'},#desc
    }

def dl_cvi(dl_obj,append_domain = []):
    Export_Para_quants_copy = deepcopy(Export_Para_quants)
    Export_Para_quants_copy['FIELDNAME_FIELDATTR']['nguyen_nhan']['skip_field'] = False
    Export_Para_quants_copy['FIELDNAME_FIELDATTR']['tvcv_id']['string'] = u'Loại'
    filename = 'cvi'
    name = "%s%s" % (filename, '.xls')
    wb =  download_model(dl_obj,
                         Export_Para=Export_Para_quants_copy,
                         append_domain=append_domain
                        )
    return wb,name


def  write_before_title (kargs):
    worksheet = kargs['worksheet']
    row_index_before_title = kargs['row_index_before_title']
    col_index_before_title = kargs['col_index_before_title']
    noi_dung = kargs['noi_dung']
    style = kargs.get('style',normal_border_style_not_border)
    worksheet.write(row_index_before_title, col_index_before_title, noi_dung,style)
    
    
LOAI_REC_=OrderedDict([(u'Sự Cố',{'noi_dung':u'A. TÌNH HÌNH HƯ HỎNG, SỰ CỐ TRÊN MẠNG:'}),
           (u'Công Việc',{'noi_dung':u'B. TÌNH HÌNH THAY ĐỔI THIẾT BỊ VÀ DỊCH VỤ MẠNG:'})
           ])
def generate_easyxf (font='Times New Roman', bold = False,underline=False, height=12, vert = False,horiz = False):
    fonts = []
    fonts.append('name %s'%font)
    if underline:
        fonts.append('underline on')
    if bold:
        fonts.append('bold on')
    fonts.append('height %s'%(height*20))
    font = 'font: ' + ','.join(fonts)
    aligns = []
    if vert:
        aligns.append('vert %s'%vert)
    if horiz:
        aligns.append('horiz %s'%horiz)
    if aligns:
        align = 'align:  ' + ','.join(aligns)
        font = font + '; ' + align
    return font
normal_13_style = xlwt.easyxf(generate_easyxf(vert = 'center',height=13))
def write_all_row(fixups,dl_obj,set_cols_width):
    needdata = {}
    wb = xlwt.Workbook()
    ws = wb.add_sheet(u'First',)#cell_overwrite_ok=True
    if set_cols_width:
        for col,width in enumerate(set_cols_width):
            ws.col(col).width =  width
    fixups = OrderedDict(fixups)
    instance_dict = {}
    needdata['instance_dict'] = instance_dict
    for f_name,field_attr in fixups.items():
        a_field_dict = {}
        xrange = field_attr.get('range')
        offset = field_attr.get('offset',1)
        if callable(offset):
            offset = offset(needdata)
        style = field_attr.get('style',normal_13_style)
        if xrange[0]=='auto':
            row = needdata['cr'] + offset
            xrange[0] = row
            if xrange[1] == 'auto':
                xrange[1] = row
        else:
            row = xrange[0]
        val = field_attr.get('val')
        val_func = field_attr.get('val_func')
        if val_func:
            val_kargs =  field_attr.get('val_kargs',{})
            val = val_func(ws,f_name,fixups,needdata,row,dl_obj,**val_kargs)
        
        func = field_attr.get('func')
        if func:
            kargs = field_attr.get('kargs',{})
            nrow = func(ws,f_name,fixups,needdata,row,dl_obj, **kargs)
            needdata['cr'] = needdata['cr'] + nrow + ( (offset-1) if nrow>0 else 0)
        else:
            a_field_dict['val'] = val
            instance_dict[f_name]=a_field_dict
            if val != None:
                if len(xrange) ==2:
                    ws.write(xrange[0], xrange[1], val, style)
                elif len(xrange)==4:
                    ws.write_merge(xrange[0], xrange[1],xrange[2], xrange[3], val, style)
                needdata['cr'] = xrange[0]
        height =  field_attr.get('height',400)
        if height != None:
            ws.row(row).height_mismatch = True
            ws.row(row).height = height
    return wb




def thuebaotable_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
    worksheet.write(row_index, 0, u'C. TÌNH HÌNH THUÊ BAO CẬP NHẬT MẠNG DI ĐỘNG (lúc 19h00):',header_bold_style)
    
    row_index_begin = row_index
    wb,ws,row_index = download_model(dl_obj,
             Export_Para=Export_Para_thuebao,
#              append_domain=[],
#              workbook=None,
             worksheet=worksheet,
             ROW_TITLE = row_index + 1,
             return_more_thing_for_bcn = True,
             no_gray = True,
             is_set_width = False
                             )
    return row_index - row_index_begin + 1
                             
                             

def table_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
#     cates = kargs ['cates'] 
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
                'style':header_bold_style}
                )
            if loai_record ==u'Công Việc':
                domain_loai_record = [('loai_record','in',[u'Công Việc',u'Sự Vụ'])]
            else:
                domain_loai_record = [('loai_record','=',loai_record)]
            for cate in cates:# categ_id
                Export_Para_quants_copy = deepcopy(Export_Para_quants)
                domain =[('categ_id','=',cate.id)] + domain_loai_record
                workbook,worksheet,row_index  = \
                download_model(dl_obj,
                             Export_Para=Export_Para_quants_copy,
                             append_domain=domain,
                             workbook=None,
                             worksheet=worksheet,
                             ROW_TITLE = row_index + 2,
                             return_more_thing_for_bcn = True,
                            write_before_title = write_before_title,
                            kargs_write_before_title = {'worksheet' :worksheet,
                                                                        'row_index_before_title' :row_index + 1,
                                                                        'col_index_before_title' :0,
                                                                        'noi_dung':u'%s/%s'%(cate.stt_for_report,cate.name),
                                                                        'style':bold_style_italic},
                             needdata_from_table =needdata_from_table,
                             no_gray = True
                                                               
                             )
    return row_index- row_index_begin + 1
bbbg_normal_style = xlwt.easyxf(generate_easyxf(bold=True,height=16, vert = 'center',horiz = 'center'))
center_nomal_style = xlwt.easyxf(generate_easyxf(height=12, vert = 'center',horiz = 'center'))
def hom_nay_(ws,f_name,fixups,needdata,row,dl_obj):
    return u'Ngày ' + Convert_date_orm_to_str(dl_obj.date,format_date = '%d/%m/%Y') 



def dl_bcn(dl_obj,append_domain = []):
    filename = 'bcn_cate'
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
                 ('table',{'range':['auto', 0],'val':None,'func':table_ ,'offset':2 }),
                 ('thuebaotable',{'range':['auto', 0],'val':None,'func':thuebaotable_ }),
                 ('pho_dai_vthcm',{'range':['auto', 1],'val':u'Phó đài VT HCM',}),
                 ('tphcm',{'range':['auto', 7],'offset':0, 'val':u' Tp. Hồ Chí Minh, ',}),
                 ]
    wb = write_all_row(fixups,dl_obj,None)
        
    return wb,name
        
    


# def download_quants_chung_sheet(dl_obj,workbook=None,
#                                 append_domain=None,
#                                 sheet_name=None):
#     filename = 'quants-%s'%dl_obj.parent_location_id.name
#     name = "%s%s" % (filename, '.xls')
#     wb =  download_model(dl_obj,
#                          Export_Para=Export_Para_quants,
#                          append_domain=append_domain,
#                          workbook=workbook,
#                          sheet_name=sheet_name)
#     return wb,name
# # def download_quants_moi_cage_moi_sheet(dl_obj):
# #     filename = 'quants_moi_cate_moi_sheet%s'%dl_obj.parent_location_id.name
# #     name = "%s%s" % (filename, '.xls')
# #     Quant = request.env['stock.quant']#.search([])
# #     cates = Quant.search([]).mapped('categ_id')
# #     workbook = xlwt.Workbook()
# #     for cate in cates:
# #         download_quants_chung_sheet(dl_obj,workbook=workbook,append_domain=[('categ_id','=',cate.id)],sheet_name=cate.name)
# #     return workbook,name
# def download_quants_moi_cage_moi_sheet(dl_obj):
#     filename = 'quants_moi_cate_moi_sheet%s'%dl_obj.parent_location_id.name
#     name = "%s%s" % (filename, '.xls')
#     Quant = request.env['stock.quant']#.search([])
#     cates = Quant.search([]).mapped('categ_id')
#     workbook = xlwt.Workbook()
#     for cate in cates:
# #         download_quants_chung_sheet(dl_obj,workbook=workbook,append_domain=[('categ_id','=',cate.id)],sheet_name=cate.name)
#         download_model(dl_obj,
#                          Export_Para=Export_Para_quants,
#                          append_domain=[('categ_id','=',cate.id)],
#                          workbook=workbook,
#                          sheet_name=cate.name)
#     return workbook,name

