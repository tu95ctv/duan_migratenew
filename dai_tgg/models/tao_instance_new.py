 # -*- coding: utf-8 -*-
import re
import xlrd
import time
import datetime
from odoo.exceptions import UserError
from odoo import  fields
import base64
from copy import deepcopy
import logging
from unidecode import unidecode
_logger = logging.getLogger(__name__)
from odoo.osv import expression
import sys
VERSION_INFO   = sys.version_info[0]
def get_or_create_object_has_x2m (self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False, x2m_key=[]):
    
    if x2m_key:
        x2m_key_first = x2m_key[0]
        key_first_values = search_dict[x2m_key_first]
        result = []
        for key_first_value in key_first_values:
            search_dict[x2m_key_first] = key_first_value
            object = get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search)
            result.append(object.id)
            
        return [(6,False,result)]
    else:
        return get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search).id



        

def get_or_create_object_sosanh(self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False):
    
    
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
    else:
        this_model_noti_dict = None
    if inactive_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
    domain = []
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain.append(tuple_in)
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
        search_dict.update(write_dict)
        #print '***search_dict***',search_dict
        created_object = self.env[class_name].create(search_dict)
        if this_model_noti_dict !=None:
            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
        return_obj =  created_object
    else:
        if not is_must_update:
            is_write = False
            for f_name in write_dict:
                field_dict_val = write_dict[f_name]
                orm_field_val = getattr(searched_object, f_name)
                try:
                    converted_orm_val_to_dict_val = getattr(orm_field_val, 'id', orm_field_val)
                    if converted_orm_val_to_dict_val == None: #recorderset.id ==None when recorder sset = ()
                        converted_orm_val_to_dict_val = False
                except:#not singelton
                    pass
                if isinstance(orm_field_val, datetime.date):
                    converted_orm_val_to_dict_val = fields.Date.from_string(orm_field_val)
                if converted_orm_val_to_dict_val != field_dict_val:
                    is_write = True
                    break
        else:
            is_write = True
        if is_write:
            searched_object.write(write_dict)
            if this_model_noti_dict !=None:
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
        else:#'not update'
            if this_model_noti_dict !=None:
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        return_obj = searched_object
    return return_obj

EMPTY_CHAR = [u'',u' ',u'\xa0']
def check_is_string_depend_python_version(val):
    if VERSION_INFO==2:
        check_str = isinstance(val,unicode) or isinstance(val,str)
    else:
        check_str =  isinstance(val,str)
    return check_str
    
def empty_string_to_False(readed_xl_value):
    if VERSION_INFO==2:
        check_str = isinstance(readed_xl_value,unicode) or isinstance(readed_xl_value,str)
    else:
        check_str =  isinstance(readed_xl_value,str)
    
    if check_str :
        if readed_xl_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_xl_value)
        if not rs:
            return False
    return readed_xl_value





# def active_function(val):
#     return False if val ==u'na' else True

def read_merge_cell(sheet,row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            break
    val = sheet.cell_value(row,col)
    return val
def read_excel_cho_field(sheet, row, col_index,merge_tuple_list):
    #print 'row','col',row, col_index,sheet
    val = read_merge_cell(sheet, row ,col_index,merge_tuple_list)
    if VERSION_INFO==2:
        check_str = isinstance(val,unicode) or isinstance(val,str)
    else:
        check_str =  isinstance(val,str)
    if check_str:
        #sai roi
        val = val.strip()
    #print 'val',val
#     val = empty_string_to_False(val)
    return val
            
### Xong khai bao
def recursive_add_model_name_to_field_attr(self,MODEL_DICT):
    model_name = MODEL_DICT['model']
    fields= self.env[model_name]._fields
    for field_tuple in MODEL_DICT.get('fields',[]):
        f_name = field_tuple[0]
        field_attr = field_tuple[1]
        if not field_attr.get('for_excel_readonly') and f_name not in fields:
            raise UserError(u'field %s không có trong  danh sách fields của model %s'%(f_name,model_name))
#         if field_attr.get('xl_title'):
#                 field_attr[ 'xl_title_unidecode'] = unidecode(field_attr[u'xl_title'])
        if not field_attr.get('for_excel_readonly'):
            field = fields[f_name]
            field_attr['field_type'] = field.type
            if field.comodel_name:
                field_attr['model'] = field.comodel_name
                recursive_add_model_name_to_field_attr(self,field_attr)
def loop_through_fields_in_model_dict_to_add_col_index_match_xl_title(MODEL_DICT, value_may_be_title, col):
    #print 'value_may_be_title',value_may_be_title
    is_map_xl_title = False
    is_map_xl_title_foreinkey = False
    for field,field_attr in MODEL_DICT.get('fields',[]):
        if field_attr.get('set_val',None) != None:
            continue
        if field_attr.get('xl_title') ==None and field_attr.get('col_index') !=None:
            continue# cos col_index
        elif field_attr.get('xl_title'):
            if isinstance(field_attr['xl_title'], list):
                xl_title_s =  field_attr['xl_title']
            else:
                xl_title_s = [field_attr['xl_title']]
            for xl_title in xl_title_s:
                if xl_title == value_may_be_title:
                    field_attr['col_index'] = col
                    is_map_xl_title = True        
                    break
        elif field_attr.get('fields'):
            is_map_xl_title_foreinkey = loop_through_fields_in_model_dict_to_add_col_index_match_xl_title(field_attr, value_may_be_title, col)
    return is_map_xl_title or is_map_xl_title_foreinkey

def create_instance (self, MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict, main_call_create_instance = None):
    key_search_dict = {}
    update_dict = {}
    value_fields_of_instance_dicts = {}
    model_name = MODEL_DICT['model']
    if main_call_create_instance == model_name:
        needdata['value_fields_of_instance_dicts'] = value_fields_of_instance_dicts
    x2m_key = []
    for count, field_field_attr in enumerate(MODEL_DICT['fields']):
        field_name = field_field_attr[0]
        field_attr = field_field_attr[1]
        col_index = field_attr.get('col_index')
        xl_val = False
        required_valid_of_this_field = True
        field_type_of_this_model = MODEL_DICT.get('field_type')
        
        if col_index == None and field_attr.get('xl_title'):
            is_match =  False
        else:
            is_match = True
#         if field_name=='product_qty':
#             print 'col_index',col_index,"field_attr.get('xl_title')",field_attr.get('xl_title')
        #sai roi
        if not is_match:
            allow_not_match =  field_attr.get('skip_field_if_not_found_column_in_some_sheet') or (field_attr.get('sheet_allow_this_field_not_has_exel_col') and needdata['sheet_name'] in field_attr.get('sheet_allow_this_field_not_has_exel_col'))
            if not allow_not_match:
                raise UserError(u'có khai báo xl_title nhưng không match với file excel')
            #sai roi
        if field_attr.get('set_val') != None:
            xl_val = field_attr.get('set_val')
#             
#         if col_index == None and field_attr.get('xl_title') and not field_attr.get('skip_field_if_not_found_column_in_some_sheet') :
#             raise UserError(u'có khai báo xl_title nhưng không match với file excel')
#         elif  col_index == None and field_attr.get('xl_title') and field_attr.get('skip_field_if_not_found_column_in_some_sheet'):
#             xl_val = False
        elif col_index !=None: # đọc file exc
            xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
            a_field_val_dict = value_fields_of_instance_dicts.setdefault(field_name,{})
            a_field_val_dict['excel_val'] = xl_val
            xl_val = empty_string_to_False(xl_val)
            if xl_val   != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('x2m_list'):
                xl_val = xl_val.split(',')
                xl_val = map(lambda i: i.strip(),xl_val)
        elif field_attr.get('fields'):#and field_attr.get('field_type')=='many2one':
            xl_val, value_fields_of_instance_dicts_childrend, required_valid_of_this_field_childrend  = create_instance (self, field_attr, sheet, row, merge_tuple_list, needdata, noti_dict)
            a_field_val_dict = value_fields_of_instance_dicts.setdefault(field_name,{})
            a_field_val_dict['fields'] = value_fields_of_instance_dicts_childrend
#         elif func:# trường hợp không match được xl_title và có func thì bị pass à
#             pass
#         else:
#             if field_attr.get('sheet_allow_this_field_not_has_exel_col') and needdata['sheet_name'] in field_attr.get('sheet_allow_this_field_not_has_exel_col'):
#                 xl_val = False
#             else:
#                 raise UserError('KHông có col_index %s-%s'%(field_name,field_field_attr))
        a_field_val_dict = value_fields_of_instance_dicts.setdefault(field_name,{})
        a_field_val_dict['before_func_val'] = xl_val
        func =  field_attr.get('func')
        xl_val = func(xl_val, needdata) if func else xl_val
        
        
        
        if  field_attr.get('replace_string') and check_is_string_depend_python_version(xl_val):
            for pattern,repl in field_attr.get('replace_string'):
                xl_val = re.sub(pattern, repl, xl_val)
        if field_attr.get('empty_val') and xl_val in field_attr.get('empty_val'):
            xl_val = False   
        replace_val = field_attr.get('replace_val')
        if replace_val:
            replace_val_tuple = replace_val.get(needdata['sheet_name']) or replace_val.get('all')
            if replace_val_tuple:
                for k,v in replace_val_tuple:
                    if xl_val ==k:
                        xl_val = v
                        break
        if xl_val == False and  field_attr.get('default'):
            xl_val = field_attr.get('default')
        
        a_field_val_dict['val'] = xl_val
        required = field_attr.get('required',False)
        if required and xl_val==False:
            required_valid_of_this_field = False
            obj_id = False
        if not required_valid_of_this_field:
            return obj_id , value_fields_of_instance_dicts, required_valid_of_this_field
        if not field_attr.get('for_excel_readonly'):
            key_or_not = field_attr.get('key')
            if key_or_not==True:
                key_search_dict [field_name] = xl_val
            elif key_or_not == 'Both':
                key_search_dict [field_name] = xl_val
                update_dict [field_name] = xl_val
            else:
                update_dict [field_name] = xl_val
        if field_attr.get('x2m_list'):
                x2m_key.append(field_name)
    
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    obj_id = get_or_create_object_has_x2m(self, model_name, key_search_dict, update_dict,
                                is_must_update=True, noti_dict = noti_dict,
                                inactive_include_search  = inactive_include_search, x2m_key = x2m_key)
    return obj_id, value_fields_of_instance_dicts,  required_valid_of_this_field
def convert_integer(val,needdata):
    try:
        return int(val)
    except:
        return 0
    
def chon_location_id(val,needdata):
    location_id = \
    needdata['value_fields_of_instance_dicts']['location_id4']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id3']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id2']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id1']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id_goc']['val']
    return location_id
def uom_id_(val,needdata):
    if val ==False:
        return 1
    else:
        return val
def location_id_goc_(v,n):
#     lambda val, needdata: self.env['stock.location'].search([('name','=','LTK Dự Phòng')]).id
        self = n['self']
        department  = self.env['hr.department']
        department_id = department.search([('name','like','LTK')])
        department_id= department_id.id
        return get_or_create_object_has_x2m(self,'stock.location', {'name':'LTK Dự Phòng'},{'department_id':department_id})
def importthuvien(odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    for r in self:
            recordlist = base64.decodestring(r.file)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            ALL_MODELS_DICT = {
                u'stock.inventory.line': {
                'title_rows':[4,5],
                'title_rows_some_sheets':{u'XFP, SFP các loại':[2,3]},
                'begin_data_row_offset_with_title_row' :3,
                'sheet_names':[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                'model':'stock.inventory.line',
                'fields' : [
('location_id_goc', {'func':location_id_goc_,'key':False, 'for_excel_readonly' :True,"required":True}),                       
('prod_lot_id_excel_readonly',{'empty_val':[u'N/C'],'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':[u'Seri Number'],'for_excel_readonly' :True}),
# ('product_qty', {'func':lambda val, n: 1 if  (n['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'] and val > 1) else val ,'xl_title':u'Tồn kho cuối kỳ','key':False}),
('product_qty', {'key':True, 'func':lambda val, n: 1 if  (n['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'] and val > 1) else val,'replace_val':{u'XFP, SFP các loại':[(False,1)]},'xl_title':u'Tồn kho cuối kỳ','key':False,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
# ('inventory_id', {'func': lambda val,needdata:get_or_create_object_sosanh(self,'stock.inventory', {'name':needdata['sheet_name']}, {}).id,'key':False}),
('inventory_id', {'fields':[
                        ('name',{'func':lambda val,needdata:needdata['sheet_name'], 'key':True,'required': True}),
#                         ('location_id',{'fields':[('name',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id_goc']['val'], 'key':True,'required': True}),]})
                        ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id_goc']['val']})
                        ,]
    }),
('product_id',{'key':True,'required':True,
               'fields':[
                        ('name',{'func':None,'xl_title':[u'TÊN VẬT TƯ',u'Module quang'],'key':True,'required':True,'empty_val':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000']}),
                        ('type',{'set_val':'product'}),
                        ('tracking',{'func':lambda val,needdata: 'serial' if needdata['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'] !=False else 'none' }),
                        ('thiet_bi_id',{'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
                        ('brand_id',{'empty_val':[u'NA'],'fields':[('name',{'func':None,'xl_title':[u'Hãng sản xuất',u'Hãng / Model'], 'key':True,'required': True}),]}),
                        ('categ_id',{'fields':[('name',{'func':lambda val,needdata: needdata['sheet_name'], 'key':True,'required': True}),]}),
                        ('uom_id',  { 'func':uom_id_,'fields': [ 
                            ('name',{'func':lambda v,n: u'Cái' if n['sheet_name']== u'XFP, SFP các loại' else v ,
                                     'xl_title':u'Đơn vị tính' ,'key':True,'required':True,
                                      'replace_string':[('Modunle','module')],
                                      'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']
                                      }),#'set_val':u'Cái',
                          ('category_id', {'fields': [('name',{'set_val':u'Unit','key':True,'required':True})
                                                                                               ]
                                                                                  }
                                                           ),
                                                       ]
                                            }
                         ),
                        ('ghi_chu_ngay_nhap',{'func':lambda val,needdata: val if not needdata['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ngày nhập'}),
                        ('ghi_chu_ngay_xuat',{'func':lambda val,needdata: val if not needdata['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ngày xuất'}),
                        ('ghi_chu_ban_dau',{'func':lambda val,needdata: val if not needdata['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'] else False,'xl_title':u'Ghi chú'}),
                        ]
               }),  
('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':u'Phòng', 'key':True,'required': True,'sheet_allow_this_field_not_has_exel_col':[u'XFP, SFP các loại']}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id_goc']['val'], 'key':True}),
                                                ('department_id',{'key':True,'model':'hr.department', 'fields':[('name',{'key':True,'set_val':'LTK'})]})
                                                ]
                                       }), 
('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':[u'Tủ/Kệ',u'Tủ'], 'key':True,'required': True}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id1']['val'] or  needdata['value_fields_of_instance_dicts']['location_id_goc']['val']  , 'key':True}),
                                                ('department_id',{'key':True,'model':'hr.department', 'fields':[('name',{'key':True,'set_val':'LTK'})]})
                                                ]
                                       }),                                           
('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':[u'Ngăn',u'Ngăn/Kệ'], 'key':True,'required': True}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id2']['val'] or needdata['value_fields_of_instance_dicts']['location_id1']['val'] or  needdata['value_fields_of_instance_dicts']['location_id_goc']['val'], 'key':True}),
                                                ('department_id',{'key':True,'model':'hr.department', 'fields':[('name',{'key':True,'set_val':'LTK'})]})
                                                ]
                                       }),         
('location_id4',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':[u'Hộp'], 'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id3']['val'] or needdata['value_fields_of_instance_dicts']['location_id2']['val'] or needdata['value_fields_of_instance_dicts']['location_id1']['val'] or  needdata['value_fields_of_instance_dicts']['location_id_goc']['val'], 'key':True}),
                                                ('department_id',{'key':True,'model':'hr.department', 'fields':[('name',{'key':True,'set_val':'LTK'})]})
                                                ]
                                       }),  
                            
                            
                                                             
('location_id', {'func':chon_location_id, 'key':False}),
# ('pn',{'xl_title':u'Part Number','for_excel_readonly' :True}),
('prod_lot_id', {'key':True,
                  'fields':[
                    ('name',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['prod_lot_id_excel_readonly']['val'],'key':True,'required':True}),
                    ('product_id',{'func':lambda v,n:n['value_fields_of_instance_dicts']['product_id']['val'] }),
                    ('pn',{'xl_title':[u'Part Number',u'Partnumber']}),
                    ('ghi_chu_ngay_nhap',{'func':lambda v,n: n['value_fields_of_instance_dicts']['product_id']['fields']['ghi_chu_ngay_nhap']['before_func_val']}),
#                     ('ghi_chu_ngay_xuat',{'func':None,'xl_title':u'Ngày xuất'}),
#                     ('ghi_chu_ban_dau',{'func':None,'xl_title':u'Ghi chú'}),
                    ('ghi_chu_ngay_xuat',{'func':lambda v,n: n['value_fields_of_instance_dicts']['product_id']['fields']['ghi_chu_ngay_xuat']['before_func_val']}),
                    ('ghi_chu_ban_dau',{'func':lambda v,n: n['value_fields_of_instance_dicts']['product_id']['fields']['ghi_chu_ban_dau']['before_func_val']}),
                      ]
                  }),
                         ]
                },#End stock.inventory.line'
                         
                u'Thư viện công việc': {
                'inactive_include_search':True,
                'title_rows' : range(1,4), 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names':xl_workbook.sheet_names(),
                'model':'tvcv',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Công việc','key':'Both' , 'required':True } ),#'func_de_tranh_empty':lambda r:  len(r) > 2
                        ( 'loai_record',{'func':None,'set_val':u'Công Việc', 'key':False }),
                        ( 'cong_viec_cate_id',{'func':lambda val,needdata:get_or_create_object_sosanh(self, 'tvcvcate', {'name':needdata['sheet_name']}, {} ).id , 'key':False }),
                        ( 'code',{'func':None,'xl_title':u'Mã CV','key':False }),
                        ('do_phuc_tap',{'func':convert_integer,'xl_title':u'Độ phức tạp','key':False}),
                        ('don_vi',{'fields':[
                                                ('name',{'key':True, 'required':True, 'xl_title':u'Đơn vị' }),
                                                ],'key' : False, 'required' : False}),
                         ('thoi_gian_hoan_thanh',{'func':convert_integer, 'xl_title':u'Thời gian hoàn thành','key':False}),
                         ('dot_xuat_hay_dinh_ky',{'fields':[
                                                ('name',{'key':True, 'required':True,'col_index':7}),
                                                ],'key' : False,'required' : False}),  
                        ('ghi_chu',{'func':None,'xl_title':u'Ghi chú','key':False}),
                        ('children_ids',{'key':False,'required':False,
                                       'fields':[
                                                ('name',{'xl_title':u'Các công việc con',  'key':True, 'required':True, 'x2m_list':True,'skip_field_if_not_found_column_in_some_sheet':True }),
                                                ]
                                       }),  
                         ('active',{'func':lambda val, needdata: False if val ==u'na' else True,'xl_title':u'active','key':False,'skip_field_if_not_found_column_in_some_sheet':True,'use_fnc_even_cell_is_False':True}),
                      ]
                },#End stock.inventory.line'
                                  
                u'User': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': ['Sheet1'],
                'model':'res.users',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Họ và Tên','key':False,'required':True}),
                         ( 'login',{'func':None,'xl_title':u'Địa chỉ email','key':True ,'required':True}),
                        ('password',{'func':None,'required':True,'set_val':'123456'}),

                         ('phone',{'func':None,'xl_title':u'Số điện thoại','key':False}),
#                         ('cac_sep_ids',{'func':None,'xl_title':u'Cấp trên','key':False,'key_name':'login','m2m':True}),
                         ('cac_sep_ids',{'key':False,'required':False,
               'fields':[
                        ('login',{'xl_title':u'Cấp trên',  'key':True, 'required':True, 'x2m_list':True}),

                        ]
               }),  
                         ('job_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân Viên' if v==False else v }),
                        ]
               }),  
                                
                    ('department_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Bộ Phận',  'key':True, 'required': True}),
                        ]
               }),  
                                
#                         ('department_id',{'model':'hr.department','func':None,'xl_title':u'Bộ Phận','key':False}),
                      ]
                },#End stock.inventory.line'
                         
                 u'Department': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Công Ty'],
                'model':'hr.department',
                'fields' : [
                         ('name',{'func':None,'xl_title':u'công ty','key':True,'required':True}),

                        ('parent_id',{'fields':[('name',{'xl_title':u'parent_id','key':True,'required':True}),
                                                       ]
                                            }
                         ),
                        ('cong_ty_type',{'fields':[('name',{'xl_title':u'cong_ty_type','key':True,'required':True}),
                                                       ]
                                            }
                         ),
                        ('sequence_id',{'fields':[('name',{'xl_title':None,'func':lambda v,n:'sequence ' + n['value_fields_of_instance_dicts']['name']['val'] ,'key':True,'required':True}),
                                                       ]
                                            }
                         ),
                        ('default_stock_location_id',{'fields':[
                            ('name',{'xl_title':None,'func':lambda v,n: n['value_fields_of_instance_dicts']['name']['val'] + u' Dự Phòng','key':True,'required':True}),
                            ('location_id',{'fields':[('name',{'set_val':'DHCM','key':True,'required':True}),
                                                                                   ]
                                                                        }
                                                     ),                                                                                
                                                                                ]
                                                                    }
                         ),
                        
                      ]
                },#End stock.inventory.line'
                         
                }#end tag ALL_MODELS_DICT
            noti_dict = {}
            CHOOSED_MODEL_DICT = ALL_MODELS_DICT[r.type_choose]
            recursive_add_model_name_to_field_attr(self,CHOOSED_MODEL_DICT)
            for sheet_name in CHOOSED_MODEL_DICT['sheet_names']:
                MODEL_DICT = deepcopy(CHOOSED_MODEL_DICT)
                needdata = {}
                needdata['sheet_name'] = sheet_name
                needdata['self'] = self
                sheet = xl_workbook.sheet_by_name(sheet_name)
                row_title_index =None
                title_rows = MODEL_DICT.get('title_rows_some_sheets',{}).get(sheet_name)
                title_rows = title_rows or CHOOSED_MODEL_DICT['title_rows']
                for row in title_rows:
                    for col in range(0,sheet.ncols):
                        if VERSION_INFO ==2:
                            value_may_be_title = unicode(sheet.cell_value(row,col))
                        else:
                            value_may_be_title = str(sheet.cell_value(row,col))
                        is_map_xl_title = loop_through_fields_in_model_dict_to_add_col_index_match_xl_title( MODEL_DICT, value_may_be_title, col)
                        if is_map_xl_title:
                            row_title_index = row
                merge_tuple_list =  sheet.merged_cells
                if row_title_index == None:
                    raise UserError(u'row_title_index == None, không có xl_title nào match với excel')
                for c,row in enumerate(range(row_title_index + CHOOSED_MODEL_DICT.get('begin_data_row_offset_with_title_row',1), sheet.nrows)):
                    print ('row',row)
                    obj_id, value_fields_of_instance_dicts, required = create_instance( self, MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict, main_call_create_instance=CHOOSED_MODEL_DICT['model'])
            r.log= noti_dict
            

            
            
