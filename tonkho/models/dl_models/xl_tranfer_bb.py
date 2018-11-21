# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import os
import inspect
from xlutils.filter import process,XLRDReader,XLWTWriter
import xlrd, xlwt
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str
from collections import  OrderedDict
from odoo.addons.downloadwizard.models.dl_models.dl_model import  write_all_row,generate_easyxf
# from odoo.addons.tonkho.controllers.controllers import  download_ml_for_bb
# from odoo.addons.tonkho.controllers.controllers import  get_width

from odoo.addons.tonkho.models.dl_models.dl_model_ml import  download_ml_for_bb
from odoo.addons.downloadwizard.models.dl_models.dl_model import  get_width
from odoo.addons.downloadwizard.models.dl_models.dl_model import  vert_center_style,bold_center_style,center_style,center_underline_style,bbbg_style



# generate_easyxf (font='Times New Roman', bold = False, height=240, vert = 'center',horiz = 'center')

# vert_center_style = xlwt.easyxf(generate_easyxf(vert = 'center'))
# bold_center_style = xlwt.easyxf(generate_easyxf(bold=True,vert = 'center',horiz='center'))
# center_style = xlwt.easyxf(generate_easyxf(vert = 'center',horiz='center'))
# center_underline_style = xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))
# bbbg_style = xlwt.easyxf(generate_easyxf(bold=True,height=16, vert = 'center',horiz = 'center'))

def write_merge_cell(row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            return crange
    return None
# def copy2(wb):
#     w = XLWTWriter()
#     process(
#         XLRDReader(wb,'unknown.xls'),
#         w
#         )
#     return w.output[0][1], w.style_list
def ong_ba_(ws,f_name,fixups,needdata,row,dl_obj,source_member_ids='source_member_ids'):
#     alist = [(u'Ông: Nguyễn Đức Tứ',u'CV: Nhân viên'),(u'Ông: Nguyễn Đức Tính',u'CV: Sếp')]
#     row = fixups['ddbg']['range'][0] + 1
#     row = needdata['cr'] + offset
    nrow = 0
    for c,i in enumerate(getattr(dl_obj,source_member_ids)):
        nrow +=1
        ws.write_merge(row + c,row + c,1,2,u'Ông/bà: %s'%i.name,vert_center_style)
        chuc_vu_don_vis =[]
        if i.job_id.name:
            chuc_vu_don_vis.append(i.job_id.name)
        if i.parent_id.name:
            chuc_vu_don_vis.append(i.parent_id.name)
        if chuc_vu_don_vis: 
            ws.write_merge(row + c,row + c,3,7,u'C/v: %s'%(u' '.join(chuc_vu_don_vis)),vert_center_style)
#         ws.write_merge(row + c,row + c,5,7,u'                 Đ/v: %s'%i.parent_id.name,vert_center_style)
    return nrow
def table_(ws,f_name,fixups,needdata,row,dl_obj,IS_SET_TT_COL=False,all_tot_and_ghom_all_tot=False):
#     row = needdata['cr'] + offset
    nrow = download_ml_for_bb(dl_obj, worksheet=ws,row_index=row, IS_SET_TT_COL = IS_SET_TT_COL, all_tot_and_ghom_all_tot=all_tot_and_ghom_all_tot)
#     needdata['cr'] = row + nrow - 1
    return nrow

def to_trinh_(ws,f_name,fixups,needdata,row,dl_obj):
    return (u'Căn cứ vào tờ trình ' + dl_obj.totrinh_id.get_names_for_report() )if  dl_obj.totrinh_id else u''
def ly_do_(ws,f_name,fixups,needdata,row,dl_obj):
    return (u'Lý do: ' + dl_obj.ly_do )if  dl_obj.ly_do else u''


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
def ky_ten_cac_ben_(ws,f_name,fixups,needdata,row,dl_obj,source_member_ids='source_member_ids',is_not_show = False,type='name'
                    ,empty_force = False):
    if is_not_show:
        return None
    source_member_ids_obj = getattr(dl_obj,source_member_ids)
    source_member_ids = source_member_ids_obj.mapped(type)
    
    if source_member_ids :
        source_member_ids = (u' '*10).join(source_member_ids)
    else:
        if source_member_ids_obj and empty_force:
            return ' '
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
def offset_job_ben_t4_(n,field_name='job_ben_t3',offset_default=1):
    if n['instance_dict'][field_name]['val'] != None:
        offset = 0
    else:
        offset = offset_default
    return offset
def xac_nhan_lanh_dao_(ws,f_name,fixups,needdata,row,dl_obj):
    if dl_obj.is_not_show_y_kien_ld:
        return None
    else:
        return u'XÁC NHẬN CỦA LĐ ĐÀI'

def write_xl_bb(dl_obj):
    
    all_tot_and_ghom_all_tot = set(dl_obj.move_line_ids.mapped('tinh_trang')) ==set(['tot']) and   dl_obj.is_ghom_tot
    IS_SET_TT_COL = dl_obj.is_set_tt_col
#     IS_SET_TT_COL and not all_tot_and_ghom_all_tot

#     cols = []
#     set_cols_width = ['sl', 'pr', 'pn', 'sl', 'dvt', 'sn', 'tt','gc']
    if  IS_SET_TT_COL and not all_tot_and_ghom_all_tot :
        set_cols_width = [4,21,16,6,5,16,6,16]
    else:
        set_cols_width = [4,21,16,6,5,16,22,0]
    set_cols_width = map(get_width,set_cols_width)
    
    fixups =[  
                    ('trung_tam1',{'range':[0,0,0,2],'val':u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=11, vert = 'center',horiz = 'center'))}),
                    ('trung_tam2',{'range':[1,1,0,2],'val':u'ĐÀI VIỄN THÔNG HCM', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                    ('chxhcnvn',{'range':[0,0,3,7],'val':u'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=12, vert = 'center',horiz = 'center'))}),
                    ('dltdhp',{'range':[1,1,3,7],'val':u'Độc lập - Tự do - Hạnh Phúc', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                    ('so',{'range':[2,2,0,2],'val':u'Số: %s/%s-%s'%(dl_obj.stt_trong_bien_ban_in,dl_obj.ban_giao_or_nghiem_thu,dl_obj.department_id.short_name), 'style':xlwt.easyxf(generate_easyxf(height=12, vert = 'center',horiz = 'center'))}),
                    ('bbg',{'range':[3,3,0,7],'val':u'BIÊN BẢN BÀN GIAO VẬT TƯ', 'style':bbbg_style,'height':1119,'off_set':1}),
                    ('to_trinh',{'range':[5,5,0,7],'val':None, 'val_func': to_trinh_ ,'height':600}),
                    ('hom_nay',{'range':[6,0],'val':None, 'val_func': hom_nay_ }),
                    ('ddbg',{'range':[8,0],'val':u'Đại diện bên giao (%s)'%(dl_obj.location_id.partner_id_of_stock_for_report.name)}),
                    ('ong_ba',{'range':['auto', 0],'val':None, 'func':ong_ba_}),
                    ('ddbn',{'range': ['auto', 0],'val':u'Đại diện bên nhận (%s)'%(dl_obj.location_dest_id.partner_id_of_stock_for_report.name),'offset':2}),
                    ('ong_ba2',{'range':['auto', 0], 'val':None,  'func':ong_ba_,'kargs':{'source_member_ids':'dest_member_ids'}}),
                    ('ly_do',{'range': ['auto', 'auto', 0,7],'val':None,'val_func':ly_do_,}),
                    ('bg',{'range': ['auto', 0],'val':u'Chúng tôi đã tiến hành bàn giao vật tư bên dưới'}),
                    ('table',{'range':['auto', 0],'val':None,'func':table_ ,'offset':2 ,'kargs': {'IS_SET_TT_COL':IS_SET_TT_COL,'all_tot_and_ghom_all_tot':all_tot_and_ghom_all_tot}}),
                    ('tinh_trang_vat_tu',{'range': ['auto', 0],'val':None,'val_func':tinh_trang_vat_tu_,'offset':2}),
                    ('so_ban_in',{'range': ['auto', 0],'val':u'Biên bản được lập thành %s bản. Bên giao giữ %s bản. Bên nhận giữ %s bản'%(dl_obj.so_ban_in,dl_obj.ben_giao_giu,dl_obj.ben_nhan_giu),'offset':1}),
                  
                    ('dai_dien_ben_giao',{'range': ['auto','auto',0,2],'val':u'ĐẠI DIỆN BÊN GIAO','offset':3, 'style':bold_center_style}),
                    ('dai_dien_ben_nhan',{'range': ['auto','auto',4,7],'val':u'ĐẠI DIỆN BÊN NHẬN','offset':0, 'style':bold_center_style}),
                    
                    ('job_ben_giao',{'range': ['auto','auto',0,2],'val':None,'offset':1,'val_func':ky_ten_cac_ben_,'val_kargs':{'type':'job_id.name','empty_force':True},'style':center_style}),
                    ('job_ben_nhan',{'range': ['auto','auto',4,7],'val':None,'offset':0,'val_func':ky_ten_cac_ben_, 'val_kargs':{'source_member_ids':'dest_member_ids','type':'job_id.name','empty_force':True},'style':center_style}),
                    ('ky_ten_ben_giao',{'range': ['auto','auto',0,2],'val':None,'offset':5,'val_func':ky_ten_cac_ben_, 'style':bold_center_style}),
                    ('ky_ten_ben_nhan',{'range': ['auto','auto',4,7],'val':None,'offset':0,
                                        'val_func':ky_ten_cac_ben_,'val_kargs':{'source_member_ids':'dest_member_ids'}, 'style':bold_center_style}),
                   
                    
                    ('dai_dien_ben_t3',{'range': ['auto','auto',0,2],'val':None,'offset':3, 'style':bold_center_style,'val_func':dai_dien_ben_t3_,'val_kargs':{'title_ben_thu_3':'title_ben_thu_3'}}),
                    ('dai_dien_ben_t4',{'range': ['auto','auto',4,7],'val':None,'offset':offset_job_ben_t4_,'offset_kargs':{'field_name':'dai_dien_ben_t3','offset_default':3}, 'style':bold_center_style,'val_func':dai_dien_ben_t3_,'val_kargs':{'title_ben_thu_3':'title_ben_thu_4'}}),
                    
                    ('job_ben_t3',{'range': ['auto','auto',0,2],'val':None,'offset':1,'val_func':ky_ten_cac_ben_,'val_kargs':{'type':'job_id.name','source_member_ids':'ben_thu_3_ids','empty_force':True},'style':center_style}),
                    ('job_ben_t4',{'range': ['auto','auto',4,7],'val':None,'val_func':ky_ten_cac_ben_, 'offset':offset_job_ben_t4_,'val_kargs':{'source_member_ids':'ben_thu_4_ids','type':'job_id.name','empty_force':True},'style':center_style}),
                    
                    ('ky_ten_ben_t3',{'range': ['auto','auto',0,2],'val':None,'offset':5,'val_func':ky_ten_cac_ben_, 'style':bold_center_style,'val_kargs':{'source_member_ids':'ben_thu_3_ids'}}),
                    ('ky_ten_ben_t4',{'range': ['auto','auto',4,7],'val':None,'offset':offset_job_ben_t4_,'offset_kargs':{'field_name':'ky_ten_ben_t3','offset_default':5},
                                        'val_func':ky_ten_cac_ben_, 'style':bold_center_style,'val_kargs':{'source_member_ids':'ben_thu_4_ids'}
                                        }, ),
                    ('xac_nhan_lanh_dao',{'range': ['auto','auto',0,7],'val':None,'val_func': xac_nhan_lanh_dao_,'offset':2, 'style':bold_center_style}),
                    ('ld_dai_id',{'range': ['auto','auto',0,7],'val':None,'offset':5, 'style':bold_center_style,
                                   'val_func':ky_ten_cac_ben_, 'style':bold_center_style,'val_kargs':{'source_member_ids':'lanh_dao_id','is_not_show':dl_obj.is_not_show_y_kien_ld}
                                  }),
             ]
    
    wb = write_all_row(fixups,dl_obj,set_cols_width)
    filename = '%s_%s_%s'%(dl_obj.department_id.short_name,dl_obj.ban_giao_or_nghiem_thu,dl_obj.stt_trong_bien_ban_in)
    name = "%s%s" % (filename, '.xls')
    return wb,name
   
        
    
#     for col in range(1,readsheet.ncols):
#         width = copied_ws.col(col).width
#         cols.append(width)
#     print ('cols',cols)

#     merge_tuple_list =  readsheet.merged_cells

    
    
#     wb.save(u'C:/D4/test_folder/Mẫu BBBG 2018hehe.xls')
    
    


