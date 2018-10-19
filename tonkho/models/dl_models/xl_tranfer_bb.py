# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import os
import inspect
from xlutils.filter import process,XLRDReader,XLWTWriter
import xlrd, xlwt
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str
from collections import  OrderedDict

# from odoo.addons.tonkho.controllers.controllers import  download_ml_for_bb
# from odoo.addons.tonkho.controllers.controllers import  get_width

from odoo.addons.tonkho.models.dl_models.dl_model_ml import  download_ml_for_bb
from odoo.addons.tonkho.models.dl_models.dl_model import  get_width




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

# generate_easyxf (font='Times New Roman', bold = False, height=240, vert = 'center',horiz = 'center')

normal_style = xlwt.easyxf(generate_easyxf(vert = 'center'))
normal_13_style = xlwt.easyxf(generate_easyxf(vert = 'center',height=13))

# bold_normal_style = xlwt.easyxf("font:  name Times New Roman, bold on,height 240")
bold_center_style = xlwt.easyxf(generate_easyxf(bold=True,vert = 'center',horiz='center'))

# center_normal_style = xlwt.easyxf("font: name Times New Roman,underline on,bold on, height 240; align:  vert centre, horiz center;")
center_normal_style = xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))
# bbbg_normal_style = xlwt.easyxf("font: name Times New Roman,bold on, height 320; align:  vert centre, horiz center;")
bbbg_normal_style = xlwt.easyxf(generate_easyxf(bold=True,height=16, vert = 'center',horiz = 'center'))
# def generate_easyxf ():

def write_merge_cell(row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            return crange
    return None
def copy2(wb):
    w = XLWTWriter()
    process(
        XLRDReader(wb,'unknown.xls'),
        w
        )
    return w.output[0][1], w.style_list
def ong_ba_(ws,f_name,fixups,needdata,row,dl_obj,source_member_ids='source_member_ids'):
#     alist = [(u'Ông: Nguyễn Đức Tứ',u'CV: Nhân viên'),(u'Ông: Nguyễn Đức Tính',u'CV: Sếp')]
#     row = fixups['ddbg']['range'][0] + 1
#     row = needdata['cr'] + offset
    nrow = 0
    for c,i in enumerate(getattr(dl_obj,source_member_ids)):
        nrow +=1
        ws.write_merge(row + c,row + c,1,2,u'Ông/bà: %s'%i.name,normal_style)
        ws.write_merge(row + c,row + c,3,7,u'C/v: %s %s'%(i.job_id.name,i.parent_id.name),normal_style)
#         ws.write_merge(row + c,row + c,5,7,u'                 Đ/v: %s'%i.parent_id.name,normal_style)
    return nrow
def table_(ws,f_name,fixups,needdata,row,dl_obj,IS_SET_TT_COL=False,all_tot_and_ghom_all_tot=False):
#     row = needdata['cr'] + offset
    nrow = download_ml_for_bb(dl_obj, worksheet=ws,row_index=row, IS_SET_TT_COL = IS_SET_TT_COL, all_tot_and_ghom_all_tot=all_tot_and_ghom_all_tot)
#     needdata['cr'] = row + nrow - 1
    return nrow

def to_trinh_(ws,f_name,fixups,needdata,row,dl_obj):
    return (u'Căn cứ vào tờ trình ' + dl_obj.totrinh_id.get_names_for_report() )if  dl_obj.totrinh_id else u''

def hom_nay_(ws,f_name,fixups,needdata,row,dl_obj):
    return u'Hôm nay, ngày: ' + convert_odoo_datetime_to_vn_str(dl_obj.date,format='%d/%m/%Y') + u', Tại: ' + dl_obj.noi_ban_giao.name
def tinh_trang_vat_tu_(ws,f_name,fixups,needdata,row,dl_obj):
    all_tot = set(dl_obj.move_line_ids.mapped('tinh_trang')) ==set(['tot']) 
    all_hong = set(dl_obj.move_line_ids.mapped('tinh_trang')) ==set(['hong']) 
    if all_tot:
        return u'Tình trạng vật tư : Tốt'
    if all_hong:
        return u'Tình trạng vật tư : Hỏng'
    return None
def ky_ten_cac_ben_(ws,f_name,fixups,needdata,row,dl_obj,source_member_ids='source_member_ids',is_not_show = False):
    if is_not_show:
        return None
    source_member_ids = getattr(dl_obj,source_member_ids)
    source_member_ids = source_member_ids.mapped('name')
    if source_member_ids:
        source_member_ids = (u' '*10).join(source_member_ids)
    else:
        source_member_ids = None
    return source_member_ids

def dai_dien_ben_t3_(ws,f_name,fixups,needdata,row,dl_obj,title_ben_thu_3='title_ben_thu_3'):
    title_ben_thu_3 = getattr(dl_obj,title_ben_thu_3).name
    if title_ben_thu_3:
        return title_ben_thu_3
    else:
        return None
def offset_ky_ten_ben_t4_(n):
    if n['instance_dict']['ky_ten_ben_t3']['val'] != None:
        offset = 0
    else:
        offset = 5
    return offset
def xac_nhan_lanh_dao_(ws,f_name,fixups,needdata,row,dl_obj):
    if dl_obj.is_not_show_y_kien_ld:
        return None
    else:
        return u'XÁC NHẬN CỦA LĐ ĐÀI'
    
def write_xl_bb(dl_obj):
    all_tot_and_ghom_all_tot = set(dl_obj.move_line_ids.mapped('tinh_trang')) ==set(['tot']) and   dl_obj.is_ghom_tot
    IS_SET_TT_COL = dl_obj.is_set_tt_col
    IS_SET_TT_COL and not all_tot_and_ghom_all_tot
    needdata = {}
    wb = xlwt.Workbook()
    ws = wb.add_sheet(u'First',)#cell_overwrite_ok=True
#     cols = []
#     set_cols_width = ['sl', 'pr', 'pn', 'sl', 'dvt', 'sn', 'tt','gc']
    if  IS_SET_TT_COL and not all_tot_and_ghom_all_tot :
        set_cols_width = [4,21,16,6,5,16,6,16]
    else:
        set_cols_width = [4,21,16,6,5,16,22,0]
        
    set_cols_width = map(get_width,set_cols_width)
#     for col in range(1,readsheet.ncols):
#         width = copied_ws.col(col).width
#         cols.append(width)
#     print ('cols',cols)
    for col,width in enumerate(set_cols_width):
#         width = copied_ws.col(col).width
        ws.col(col).width =  width
#     merge_tuple_list =  readsheet.merged_cells

    fixups =[  
                    ('trung_tam1',{'range':[0,0,0,2],'val':u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=11, vert = 'center',horiz = 'center'))}),
                    ('trung_tam2',{'range':[1,1,0,2],'val':u'ĐÀI VIỄN THÔNG HCM', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                    ('chxhcnvn',{'range':[0,0,3,7],'val':u'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=12, vert = 'center',horiz = 'center'))}),
                    ('dltdhp',{'range':[1,1,3,7],'val':u'Độc lập - Tự do - Hạnh Phúc', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                    ('so',{'range':[2,2,0,2],'val':u'Số: %s/%s-%s'%(dl_obj.stt_trong_bien_ban_in,dl_obj.ma_bien_ban,dl_obj.department_id.short_name), 'style':xlwt.easyxf(generate_easyxf(height=12, vert = 'center',horiz = 'center'))}),
                    ('bbg',{'range':[3,3,0,7],'val':u'BIÊN BẢN BÀN GIAO VẬT TƯ', 'style':bbbg_normal_style,'height':1119,'off_set':1}),
                    ('to_trinh',{'range':[5,5,0,7],'val':None, 'val_func': to_trinh_ ,'height':600}),
                    ('hom_nay',{'range':[6,0],'val':None, 'val_func': hom_nay_ }),
                    ('ddbg',{'range':[8,0],'val':u'Đại diện bên giao (%s)'%(dl_obj.location_id.partner_id_of_stock_for_report.name)}),
                    ('ong_ba',{'range':['auto', 0],'val':None, 'func':ong_ba_}),
                    ('ddbn',{'range': ['auto', 0],'val':u'Đại diện bên nhận (%s)'%(dl_obj.location_dest_id.partner_id_of_stock_for_report.name),'offset':2}),
                    ('ong_ba2',{'range':['auto', 0], 'val':None,  'func':ong_ba_,'kargs':{'source_member_ids':'dest_member_ids'}}),
                    ('bg',{'range': ['auto', 0],'val':u'Chúng tôi đã tiến hành bàn giao vật tư bên dưới'}),
                    ('table',{'range':['auto', 0],'val':None,'func':table_ ,'offset':2 ,'kargs': {'IS_SET_TT_COL':IS_SET_TT_COL,'all_tot_and_ghom_all_tot':all_tot_and_ghom_all_tot}}),
                    ('tinh_trang_vat_tu',{'range': ['auto', 0],'val':None,'val_func':tinh_trang_vat_tu_,'offset':2}),
                    ('so_ban_in',{'range': ['auto', 0],'val':u'Biên bản được lập thành 04 bản có giá trị như nhau.','offset':1}),
                    ('dai_dien_ben_giao',{'range': ['auto','auto',0,2],'val':u'ĐẠI DIỆN BÊN GIAO','offset':3, 'style':bold_center_style}),
                    ('dai_dien_ben_nhan',{'range': ['auto','auto',4,7],'val':u'ĐẠI DIỆN BÊN NHẬN','offset':0, 'style':bold_center_style}),
                    
                    ('ky_ten_ben_giao',{'range': ['auto','auto',0,2],'val':None,'offset':5,'val_func':ky_ten_cac_ben_, 'style':bold_center_style}),
                    ('ky_ten_ben_nhan',{'range': ['auto','auto',4,7],'val':None,'offset':0,
                                        'val_func':ky_ten_cac_ben_,'val_kargs':{'source_member_ids':'dest_member_ids'}, 'style':bold_center_style}),
                    ('dai_dien_ben_t3',{'range': ['auto','auto',0,2],'val':None,'offset':3, 'style':bold_center_style,'val_func':dai_dien_ben_t3_,'val_kargs':{'title_ben_thu_3':'title_ben_thu_3'}}),
                    ('dai_dien_ben_t4',{'range': ['auto','auto',4,7],'val':None,'offset':0, 'style':bold_center_style,'val_func':dai_dien_ben_t3_,'val_kargs':{'title_ben_thu_3':'title_ben_thu_4'}}),
                   
                    ('ky_ten_ben_t3',{'range': ['auto','auto',0,2],'val':None,'offset':5,'val_func':ky_ten_cac_ben_, 'style':bold_center_style,'val_kargs':{'source_member_ids':'ben_thu_3_ids'}}),
                    ('ky_ten_ben_t4',{'range': ['auto','auto',4,7],'val':None,'offset':offset_ky_ten_ben_t4_,
                                        'val_func':ky_ten_cac_ben_, 'style':bold_center_style,'val_kargs':{'source_member_ids':'ben_thu_4_ids'}
                                        }, ),
                    ('xac_nhan_lanh_dao',{'range': ['auto','auto',0,7],'val':None,'val_func': xac_nhan_lanh_dao_,'offset':2, 'style':bold_center_style}),
                    ('ld_dai_id',{'range': ['auto','auto',0,7],'val':None,'offset':5, 'style':bold_center_style,
                                   'val_func':ky_ten_cac_ben_, 'style':bold_center_style,'val_kargs':{'source_member_ids':'lanh_dao_id','is_not_show':dl_obj.is_not_show_y_kien_ld}
                                  }),
             ]
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
                
        height =  field_attr.get('height')
        if height != None:
            ws.row(row).height_mismatch = True
            ws.row(row).height = height
            
    filename = '%s_%s_%s'%(dl_obj.stt_trong_bien_ban_in,dl_obj.ma_bien_ban,dl_obj.department_id.short_name)
    name = "%s%s" % (filename, '.xls')
    return wb,name
#     wb.save(u'C:/D4/test_folder/Mẫu BBBG 2018hehe.xls')
    
    


