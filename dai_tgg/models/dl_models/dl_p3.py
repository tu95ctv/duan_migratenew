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
from odoo.addons.downloadwizard.models.dl_models.dl_model import  write_all_row,generate_easyxf
from odoo.addons.downloadwizard.models.dl_models.dl_model import  get_width
from odoo.addons.downloadwizard.models.dl_models.dl_model import  stt_
from odoo.addons.downloadwizard.models.dl_models.dl_model import  header_bold_style,bold_style_italic,bold_style,normal_style,bbbg_normal_style,center_nomal_style
from dateutil.relativedelta import relativedelta

from odoo.addons.dai_tgg.mytools import  convert_date_odoo_to_str_vn_date, convert_utc_to_gmt_7
import datetime
# def get_width(num_characters):
#     return int((1+num_characters) * 256)

# def stt_(v,needdata): 
#     v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
#     return v  






# FIELDNAME_FIELDATTR_cvi =OrderedDict( [
#           ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
#           ('department_id',{}),
#           ('loai_record',{}),
#           ('categ_id',{}),
#           ('thiet_bi_id',{}),
#           ('tvcv_id',{'string': lambda needdata_from_table: u'Loại sự cố' if  needdata_from_table['loai_record'] == u'Sự Cố' else u'Loại CV/Sự vụ'}),
#           ('noi_dung',{}),
#           ('nguyen_nhan',{ 'string':u'Nguyên nhân','skip_field':lambda needdata_from_table:  needdata_from_table['loai_record'] != u'Sự Cố'}),
#           ('gio_bat_dau',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
#           ('gio_ket_thuc',{'func':lambda val,n: convert_odoo_datetime_to_vn_str(val, format='%d/%m/%Y %H:%M:%S' )}),
#                     ]
#                                      
#                                      )

FIELDNAME_FIELDATTR_cvi =OrderedDict( [
        ('stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_}),
        ('ngay_bat_dau',{'func': lambda v,n: Convert_date_orm_to_str(v),'width':get_width(10)}),
         ('code',{}),('tvcv_id_name',{'width':get_width(40)}),('noi_dung',{'width':get_width(40)}),
         ('slncl',{}),
         ('diem_tvi',{}),
         ('so_luong',{}),
         ('so_lan',{}),
         ('diemtc',{}),
         ('diemld',{}),    
                    
                    
                    ]
                                     
                                     )


def gen_domain_cvi(dl_obj,theo_sql = False):
    if not theo_sql:
        domain = [('loai_record','=',u'Công Việc')]
    else:
        where_clause_list = []
    if dl_obj.chon_thang ==u'Tháng Này':
        utc_time = datetime.datetime.now()
        vn_time = convert_utc_to_gmt_7(utc_time)
        vn_thang_nay_date_begin = vn_time.strftime('%Y-%m-01')
        vn_time_offset_thang_sau =  vn_time + relativedelta(months=1)
        vn_thang_nay_date_end = vn_time_offset_thang_sau.strftime('%Y-%m-01')
        if not theo_sql:
            domain.extend([('ngay_bat_dau','>=',vn_thang_nay_date_begin),('ngay_bat_dau','<',vn_thang_nay_date_end)])
        else:
            where_clause_list.append('cvi.ngay_bat_dau >= %s'%vn_thang_nay_date_begin)
            where_clause_list.append('cvi.ngay_bat_dau < %s'%vn_thang_nay_date_end)
    elif dl_obj.chon_thang ==u'Tháng Trước':
        utc_time = datetime.datetime.now()
        vn_time = convert_utc_to_gmt_7(utc_time)
        thang_truoc_time = vn_time + relativedelta(months=-1)
        thang_truoc_date_begin = thang_truoc_time.strftime('%Y-%m-01')
        thang_truoc_date_end = vn_time.strftime('%Y-%m-01')
        if not theo_sql:
            domain.extend([('ngay_bat_dau','>=',thang_truoc_date_begin),('ngay_bat_dau','<',thang_truoc_date_end)])
        else:
            where_clause_list.append("cvi.ngay_bat_dau >= '%s'"%thang_truoc_date_begin)
            where_clause_list.append("cvi.ngay_bat_dau < '%s'"%thang_truoc_date_end)
    else:
        if dl_obj.date:
            if not theo_sql:
                domain.append(('ngay_bat_dau','>=',dl_obj.date))
            else:
                where_clause_list.append("cvi.ngay_bat_dau >= '%s'"%dl_obj.date)
        if dl_obj.end_date:
            if not theo_sql:
                domain.append(('ngay_bat_dau','<=',dl_obj.end_date))
            else:
                where_clause_list.append("cvi.ngay_bat_dau <= '%s'"%dl_obj.end_date)
    if not theo_sql:
        return domain
    else:
        return where_clause_list



Export_Para_cvi = {
    'exported_model':'cvi',
    'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_cvi,
    'gen_domain':gen_domain_cvi,
    'search_para':{'order': 'loai_record asc'},#desc
    }



    
# 
# def  write_before_title (kargs):
#     worksheet = kargs['worksheet']
#     row_index_before_title = kargs['row_index_before_title']
#     col_index_before_title = kargs['col_index_before_title']
#     noi_dung = kargs['noi_dung']
#     style = kargs.get('style',normal_style)
#     worksheet.write(row_index_before_title, col_index_before_title, noi_dung,style)
#     




                             
                             

def table_cvi_for_user_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
#     cates = kargs ['cates'] 
    Export_Para_cvi_copy = deepcopy(Export_Para_cvi)
#     is_show_loai_record = dl_obj.env['ir.config_parameter'].sudo().get_param('dai_tgg.' + 'is_show_loai_record')
#     Export_Para_cvi_copy1['FIELDNAME_FIELDATTR']['loai_record']['skip_field'] = not is_show_loai_record
    n_row = download_model(dl_obj,
                 Export_Para=Export_Para_cvi_copy,
                 append_domain=kargs['append_domain_user_id'],
                 workbook=None,
                 worksheet=worksheet,
                 ROW_TITLE = row_index + 1,
                 return_more_thing_for_bcn = True,
                 no_gray = True,
                 OFFSET_COLUMN = 1,
                                                   
                 )
    return n_row

def sum_(worksheet,f_name,fixups,needdata,row_index,dl_obj, **kargs):
    begin_row = needdata['instance_dict']['table']['begin_row'] +2
    end_row = needdata['instance_dict']['table']['end_row']
    if end_row > begin_row:
        worksheet.write(row_index, 4, xlwt.Formula('SUM(%s%s:%s%s)'%('J',begin_row + 1,'J',end_row+1)))
    return 1# 1 row

def dl_p3_per_user(dl_obj,user_id,wb = None,tram=None):
 
    fixups =[  
                 ('trung_tam1',{'range':[0,0,0,3],'val':u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM', 'style':xlwt.easyxf(generate_easyxf(bold=True,height=11, vert = 'center',horiz = 'center'))}),
                 ('trung_tam2',{'range':[1,1,0,3],'val':u'ĐÀI VIỄN THÔNG HCM', 'style':xlwt.easyxf(generate_easyxf(bold=True,underline=True,height=12, vert = 'center',horiz = 'center'))}),
                 ('diem_tong_nhan_vien_cham_title',{'range':[5, 3],'val':u'Điểm Tổng Nhân Viên Chấm'}),
                 ('ho_ten_title',{'range':[3, 3],'val':u'Họ Tên','style':bold_style}),
                 ('ho_ten',{'range':[3, 4],'val':user_id.name}),
                 ('tram_tilte',{'range':[4, 3],'val':u'Trạm'}),
                 ('tram',{'range':[4, 4],'val':tram,'style':bold_style}),
                 ('table',{'range':[9, 0],'val':None,'func':table_cvi_for_user_ ,'offset':3 ,'kargs':{'append_domain_user_id':[('user_id','=',user_id.id)]}}),
                 ('sum',{'range':[5, 4],'func':sum_ })
                 ]
    wb = write_all_row(fixups,dl_obj,None,wb = wb,ws_name=user_id.name)
    return wb
def gen_department_id(dl_obj):
    if dl_obj.department_id:
        if dl_obj.user_has_groups('base.group_erp_manager'):
            dp_id = dl_obj.department_id
#             raise UserError(u'kakkaka 1 %s'%dl_obj.department_id.name)
#             domain.append(('department_id','=',dl_obj.department_id.id))
        else:
            dp_id = dl_obj.env.user.department_id
#             raise UserError(u'kakkaka')
#             domain.append(('department_id','=',dl_obj.env.user.department_id.id))
    else:
            dp_id = dl_obj.env.user.department_id
    return dp_id
def dl_p3(dl_obj,append_domain = []):
    
#         raise UserError(u'kakkaka 2')
#         domain.append(('department_id','=',dl_obj.env.user.department_id.id))
    
    
    dp_id =gen_department_id(dl_obj)
    cates = dl_obj.env['res.users'].search([('department_id','=',dp_id.id)])
    wb = None
    if dl_obj.chi_tiet_hay_danh_sach =='danh_sach':
        filename = u'p3_ds_%s'%dp_id.name
        wb = download_cvi_by_userlist(dl_obj)
    else:
        filename = u'p3_user_%s'%dp_id.name
        for user_id in cates:
            wb = dl_p3_per_user(dl_obj,user_id,wb,dp_id.name)
    name = "%s%s" % (filename, '.xls')
    return wb,name
    
# def download_cvi_by_userlist(dlcv_obj):
# #     dlcv_obj = request.env[model].browse(int(id))
#     where_clause = gen_domain_cvi (dlcv_obj, theo_sql = True)
#     dp_id = gen_department_id(dlcv_obj)
#     where_clause.append('hr_department.id = %s'%dp_id.id)
#     where_clause.append(u"cvi.loai_record = 'Công Việc'")
#     where_clause = 'and '.join(where_clause)
# #     sql_cmd = '''select cvi.user_id,sum(diemtc),u.login,p.name from cvi inner join res_users as u on cvi.user_id = u.id inner join res_partner as p on u.partner_id = p.id %s group by cvi.user_id ,u.login,p.name'''
#     sql_cmd = '''select cvi.user_id,sum(diemtc),res_partner.name,hr_department.name from cvi inner join res_users as u on cvi.user_id = u.id inner join hr_department as hr_department on cvi.department_id = hr_department.id  inner join res_partner  on u.partner_id = res_partner.id  %s group by cvi.user_id ,res_partner.name,hr_department.name'''
#     sql_cmd = sql_cmd%((' where ' + where_clause )if where_clause else '')
#     request.env.cr.execute(sql_cmd)
#     rsul = request.env.cr.fetchall()
#     workbook = xlwt.Workbook()
#     worksheet = workbook.add_sheet('Sheet 1')
#     normal_style = xlwt.easyxf("font:  name Times New Roman, height 240")
#     worksheet.write(0,0,'STT',normal_style)
#     worksheet.write(0,1,u'Tên',normal_style)
#     worksheet.write(0,2,u'Điểm', normal_style)
#     row_index = 1
#     stt =1
#     for u_id,diem,login,name in rsul:
#         worksheet.write(row_index,0,stt,normal_style)
#         worksheet.write(row_index,1,login,normal_style)
#         worksheet.write(row_index,2,diem,normal_style)
#         row_index += 1
#         stt +=1
#     return workbook

def download_cvi_by_userlist(dl_obj):
#     dlcv_obj = request.env[model].browse(int(id))
#     where_clause = gen_domain_cvi (dlcv_obj, theo_sql = True)
#     dp_id = gen_department_id(dlcv_obj)
#     where_clause.append('hr_department.id = %s'%dp_id.id)
#     where_clause.append(u"cvi.loai_record = 'Công Việc'")
#     where_clause = 'and '.join(where_clause)
# #     sql_cmd = '''select cvi.user_id,sum(diemtc),u.login,p.name from cvi inner join res_users as u on cvi.user_id = u.id inner join res_partner as p on u.partner_id = p.id %s group by cvi.user_id ,u.login,p.name'''
#     sql_cmd = '''select cvi.user_id,sum(diemtc),res_partner.name,hr_department.name from cvi inner join res_users as u on cvi.user_id = u.id inner join hr_department as hr_department on cvi.department_id = hr_department.id  inner join res_partner  on u.partner_id = res_partner.id  %s group by cvi.user_id ,res_partner.name,hr_department.name'''
#     sql_cmd = sql_cmd%((' where ' + where_clause )if where_clause else '')
#     request.env.cr.execute(sql_cmd)
#     rsul = request.env.cr.fetchall()
    
    domain = []
    dp_id =gen_department_id(dl_obj)
    domain = [('department_id','=',dp_id.id)]
    domain_date = gen_domain_cvi(dl_obj)
    domain.extend(domain_date)
    read_group_rsul = dl_obj.env['cvi'].read_group(domain, ['user_id', 'diemtc'], ['user_id'], orderby='id')
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Sheet 1')
    normal_style = xlwt.easyxf("font:  name Times New Roman, height 240")
    worksheet.write(0,0,'STT',normal_style)
    worksheet.write(0,1,u'Tên',normal_style)
    worksheet.write(0,2,u'Điểm', normal_style)
    row_index = 1
    stt =1
    for rs in read_group_rsul:
        worksheet.write(row_index,0,stt,normal_style)
        worksheet.write(row_index,1,str(rs['user_id'][1]),normal_style)
        worksheet.write(row_index,2,rs['diemtc'],normal_style)
        row_index += 1
        stt +=1
    return workbook




