# -*- coding: utf-8 -*-
from odoo import http
from openerp.http import request
import datetime
from odoo.tools.misc import xlwt
from odoo.addons.dai_tgg.mytools import  convert_date_odoo_to_str_vn_date
def get_width(num_characters):
    return int((1+num_characters) * 256)

normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;borders: left thin,right thin, top thin, bottom thin")
one_instance_val_dict ={}
def add_title(worksheet,FIELDNAME_FIELDATTR,cvi_fields,ROW_TITLE=0, offset_column=0):
    header_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ; pattern: pattern solid, fore_colour gray25;borders: left thin, right thin, top thin, bottom thin")
    for title_column_index, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
                title_column_index += offset_column
                f_name, FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
                is_not_model_field = FIELDATTR.get('is_not_model_field')
                split = FIELDATTR.get('split')
                if split:
                    add_title(worksheet,split, cvi_fields,ROW_TITLE=ROW_TITLE, offset_column=title_column_index)
                    offset_column += len(split)
                    continue
                if is_not_model_field:
                    f_string =FIELDATTR.get('string') or  f_name
                else:
                    field = cvi_fields[f_name]
                    f_string = field.string
                worksheet.write(ROW_TITLE, title_column_index, f_string, header_bold_style)
                width  = FIELDATTR.get('width')
                if not width :
                    width = get_width(len(f_string))
                worksheet.col(title_column_index).width = width
                
def add_1_cvi_for_1_person(worksheet,r ,FIELDNAME_FIELDATTR,stt, row_index, offset_column=0):
    for title_column_index, field_from_my_FIELDNAME_FIELDATTR in enumerate(FIELDNAME_FIELDATTR):
        title_column_index += offset_column
        f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        one_field_val = one_instance_val_dict.set_default(f_name,{})
        if is_not_model_field:
            if f_name=='stt':
                val = stt
        else:
            val = getattr(r, f_name)
            func = FIELDATTR.get('func',None)
            if func:
                val = func(val)
            if val == False:
                val = u''
        worksheet.write(row_index, title_column_index, val, normal_border_style)  
        
                     
                
def download_quants(dlcv_obj):
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(u'anh con no em',cell_overwrite_ok=True)
    worksheet.write(1,1,u'Họ và Tên',normal_border_style_not_border)
    exported_model = 'stock.quant'
    FIELDNAME_FIELDATTR = [
             ('stt',{'is_not_model_field':True,'string':u'STT'}),
#              ('ngay_bat_dau',{'func':convert_date_odoo_to_str_vn_date,'width':get_width(10)}),
             ('product_id',{'func':lambda v: v.name}),
#              ('location_id',{'func':lambda v: v.name_get_1_record()}),
             ('location_id',{'func':lambda v: v.name_get_1_record(),'split':[
                   ('tram',{'is_not_model_field':True,'string':u'Trạm'}),         
                   ('phong_may',{'is_not_model_field':True,'string':u'Phòng máy'}),
                     ('tu',{'is_not_model_field':True,'string':u'Tủ'}),
                     ('shelf',{'is_not_model_field':True,'string':u'Shelf'}),
                     ('stt_trong_self',{'is_not_model_field':True,'string':u'STT trong shelf'}),
                     ('slot',{'is_not_model_field':True,'string':u'Slot'})     
                 ]}),
              ('quantity',{'width':get_width(40)}),

#              ('noi_dung',{'width':get_width(40)}),
                        ]
    cvi_fields = request.env[exported_model]._fields
    ROW_TITLE = 0
    OFFSET_COLUMN = 0
    add_title(worksheet,FIELDNAME_FIELDATTR,cvi_fields, ROW_TITLE=ROW_TITLE, offset_column=OFFSET_COLUMN)
    person_records = request.env[exported_model].search([])
    row_index = ROW_TITLE + 1
    stt = 1
    
    for r in person_records:#request.env['cvi'].search([]):
        one_instance_val_dict = {}
        add_1_cvi_for_1_person(worksheet,r, FIELDNAME_FIELDATTR, stt, row_index, offset_column=OFFSET_COLUMN)
        row_index +=1
        stt +=  1
    return workbook
    
    
# def download_cvi(dlcv_obj):
#     num2alpha = dict(zip(range(0, 26), string.ascii_uppercase))
#     normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
#     normal_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;borders: left thin,right thin, top thin, bottom thin")
#     bold_style = xlwt.easyxf("font: bold on")
#     department_ids = dlcv_obj.department_ids
#     export_department_ids = filter_department_ids(department_ids)
#     user_ids = request.env['res.users'].search([('department_id','in',export_department_ids)])
#     workbook = xlwt.Workbook()
#     
#     offset_column = 0
#     ROW_TRUNG_TAM=0
#     ROW_SUM = ROW_TRUNG_TAM + 3
#     KEY_COL = offset_column + 3
#     VAL_COL = offset_column + 4
#     ROW_TITLE = ROW_TRUNG_TAM + 5
#     
#     FIELDNAME_FIELDATTR = [
#              ('stt',{'is_not_model_field':True,'string':u'STT'}),
#              ('ngay_bat_dau',{'func':convert_date_odoo_to_str_vn_date,'width':get_width(10)}),
#              ('code',{}),('tvcv_id_name',{'width':get_width(40)}),('noi_dung',{'width':get_width(40)}),
#              ('diem_tvi',{}),('so_luong',{}),('so_lan',{}),
#              ('diemtc',{'sum':True, 'row_sum':ROW_SUM+1,  'col_sum':VAL_COL}),
#              ('diemld',{'sum':True,'row_sum':ROW_SUM, 'col_sum':VAL_COL}),
#                         ]
#     domain = []
#     domain_date = generate_domain_date_and_department(dlcv_obj)
#     for user_id in user_ids:
#         domain_user = [('user_id','=',user_id.id),('loai_record','=',u'Công Việc')]
#         domain = expression.AND([domain_user, domain_date])
#         worksheet = workbook.add_sheet(user_id.name,cell_overwrite_ok=True)
#         add_header_TrungTamHaTangMang(worksheet,user_id,ROW_TRUNG_TAM,offset_column,normal_border_style_not_border,bold_style,ROW_SUM,KEY_COL,VAL_COL)
#         cvi_fields = request.env['cvi']._fields
#         add_title(FIELDNAME_FIELDATTR, cvi_fields, offset_column, worksheet, ROW_TITLE)
#         row_index = ROW_TITLE + 1
#         stt = 1
#         person_records = request.env['cvi'].search(domain,order='ngay_bat_dau')
#         for r in person_records:#request.env['cvi'].search([]):
#             add_1_cvi_for_1_person(worksheet,FIELDNAME_FIELDATTR, r,offset_column, stt, row_index, normal_border_style)
#             row_index +=1
#             stt +=  1
#         add_sum_info(worksheet,FIELDNAME_FIELDATTR,offset_column,num2alpha,ROW_TITLE,ROW_SUM,VAL_COL,row_index)
#     return workbook





class DownloadQuants(http.Controller):
#     @http.route('/web/binary/download_cvi_by_userlist',type='http', auth="public")
#     def download_cvi_by_userlist(self,model, id, **kw):
#         dlcv_obj = request.env[model].browse(int(id))
#         where_clause = generate_domain_date_and_department (dlcv_obj, theo_sql = True)
#         sql_cmd = '''select cvi.user_id,sum(diemtc),u.login,p.name from cvi inner join res_users as u on cvi.user_id = u.id inner join res_partner as p on u.partner_id = p.id %s group by cvi.user_id ,u.login,p.name'''
#         sql_cmd = sql_cmd%((' where ' + where_clause )if where_clause else '')
#         request.env.cr.execute(sql_cmd)
#         rsul = request.env.cr.fetchall()
#         workbook = xlwt.Workbook()
#         worksheet = workbook.add_sheet('Sheet 1')
#         normal_border_style_not_border = xlwt.easyxf("font:  name Times New Roman, height 240")
#         worksheet.write(0,0,'STT',normal_border_style_not_border)
#         worksheet.write(0,1,u'Tên',normal_border_style_not_border)
#         worksheet.write(0,2,u'Điểm', normal_border_style_not_border)
#         row_index = 1
#         stt =1
#         for u_id,diem,login,name in rsul:
#             worksheet.write(row_index,0,stt,normal_border_style_not_border)
#             worksheet.write(row_index,1,login,normal_border_style_not_border)
#             worksheet.write(row_index,2,diem,normal_border_style_not_border)
#             row_index += 1
#             stt +=1
#         response = request.make_response(None,
#             headers=[('Content-Type', 'application/vnd.ms-excel'),
#                     ('Content-Disposition', 'attachment; filename=table_cv_%s_%s.xls;'%(request.env.user.name, datetime.datetime.now().strftime('%d_%m_%H_%M')))],
#             )
#         workbook.save(response.stream)
#         return response
    
    @http.route('/web/binary/download_quants',type='http', auth="public")
    def download_quants(self,model, id, **kw):
        model = 'tonkho.downloadquants'
        dlcv_obj = request.env[model].browse(int(id))
        workbook = download_quants(dlcv_obj)
        
        
        
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=stockquantsdl_name_%s-date_%s.xls;target=blank' %(dlcv_obj.name,datetime.datetime.now().strftime('%d_%m_%H_%M')))],
            )
        workbook.save(response.stream)
        return response
    
    
    