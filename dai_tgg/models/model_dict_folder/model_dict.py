 # -*- coding: utf-8 -*-
 #Copy tu internal ham import _thu_vien
from odoo.exceptions import UserError
import datetime

# from odoo.addons.dai_tgg.models.model_dict_product import gen_product_model_dict
# from odoo.addons.dai_tgg.models.model_dict_user_department import gen_user_department_model_dict
# print ('***',type(product_model_dict))
# class self():
#     pass

# from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_product import gen_product_model_dict
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_user_department import gen_user_department_model_dict
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_tvcv import  gen_tvcv_model_dict
import re
from odoo.addons.dai_tgg.mytools import pn_replace
 
all_key_tram = 'all_key_tram'
key_ltk_dc = 'key_ltk_dc'
key_ltk_dc2 = 'key_ltk_dc2'
key_tti_dc = 'key_tti_dc'
key_137 = 'key_137'
write_xl = 'write_xl'
sml = 'sml'
key = 'key',
required = 'required'
# product = 'key_tti_dc_product'


def lot_name_key_ltk_dc_(val,needdata,self):
#     raise UserError(u'kaka')
    p_id = needdata['vof_dict']['product_id']['val']
    product_id = self.env['product.product'].browse(p_id)
    lot_name = needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or (needdata['vof_dict']['barcode_for_first_read']['val'] and  ('use barcode ' + needdata['vof_dict']['barcode_for_first_read']['val']))
#     if lot_name== UBC:
#         lot_name= lot_name + str(int(needdata['vof_dict']['stt']['val']))
    if  (lot_name ==False and  product_id.tracking=='serial'):
#         raise UserError(u'kkkkk')
        lot_name = 'unknown ' + product_id.name + '  ' + str(int(needdata['vof_dict']['stt']['val']) )
        
    return lot_name



def last_record_function_ltk_vtdc_(n,self=None):
    if not self.mode_no_create_in_main_instance:
        if n['vof_dict']['product_id']['get_or_create']== False:
            raise UserError(u'Product %s  phải được tạo từ trước'%n['vof_dict']['product_id']['fields']['name']['val'])
    gan_inventory_id_vao_needdata(n,self)
def gan_inventory_id_vao_needdata(n,self):
    if n['vof_dict']['inventory_id']['val'] and  not n.get('inventory_id'):
        n['inventory_id'] = n['vof_dict']['inventory_id']['val']
def last_import_function_(n,self):
    if not self.mode_no_create_in_main_instance:
        self.inventory_id = n['inventory_id']
def convert_float_location_(v,n):
#     return v
    if isinstance(v, float):
        v= str(int(v))
    if  v != False and isinstance(v, int):
        v = str(v)
    return v
def convert_float_to_ghi_chu_cho_sml_ngay_xuat(val):
    if isinstance(val, float):
        seconds = (val - 25569) * 86400.0
        try:
            val= datetime.datetime.utcfromtimestamp(seconds).strftime('%d/%m/%Y')
        except ValueError:# year is out of range
            pass
    return val 
def name_of_uom_id_(v,n):
    v = u'Cái' if n['sheet_name']== u'XFP, SFP các loại' else v
    if isinstance(v,str):
        v = v.capitalize()
    return v
def uom_id_137_(v,n):
    if isinstance(v,str):
        v = v.capitalize()
    else:
        v = u'Cái'
    return v
    

SHEET_CONVERT = {'TTI':{u'CHUYỂN MẠCH':u'Chuyển Mạch (IMS, Di Động)',u'IP':u'IP (VN2, VNP)',u'TRUYỀN DẪN':u'Truyền dẫn',u'GTGT': u'GTGT',u'VÔ TUYẾN' :u'Vô tuyến'}}
SHEET_CONVERT_2_BC = {u'Chuyển Mạch (IMS, Di Động)':u'Chuyển mạch',u'IP (VN2, VNP)':u'IP'}


def categ_id_tti_convert_to_ltk_(v,n,tram=None):
#         raise UserError('kdkfasdlkfjld')
    v =  n['sheet_name']
    tram_dict = SHEET_CONVERT.get(tram)
    if tram_dict:
        categ_theo_ltk =  tram_dict.get(v,v)
        return categ_theo_ltk
#         categ_theo_bc = 
    else:
        return v
    
###them self

def location_from_key_tram(v,n,self):
    key_tram = n['key_tram']
    key_tram_split = key_tram.split('_')
    tram = key_tram_split[1]
    if 'dc'  in key_tram:
        stock_location_name = tram +u' đang chạy'
    else:
        stock_location_name = tram +u' dự phòng'
    
    stock_location_id =  self.env['stock.location'].search([('name','=ilike',stock_location_name)])
    if not stock_location_id:
        raise UserError ( u' Không tồn tại stock_location ')
    return stock_location_id
def look_department_from_key_tram_(v,n,self):
    key_tram = n['key_tram']
    key_tram_split = key_tram.split('_')
    tram = key_tram_split[1]
    stock_location_id =  self.env['hr.department'].search([('name','ilike',tram)])
    return stock_location_id.id
    
def location_goc_(v,n,self):
    return location_from_key_tram(v,n,self).id
def choose_inventory_id_name(v,n,self):
    stock_location_id = location_from_key_tram(v,n,self)
    return stock_location_id.name + '-' +  ','.join(n['sheet_names'])
# end Copy tu internal ham import _thu_vien

#copy ngoai
def convert_integer(val,needdata):
    try:
        return int(val)
    except:
        return 0
def qty_(val,n):
    if val:
        val = float(int(val))
        val=  1.0 if  (n['vof_dict']['prod_lot_id_excel_readonly']['val'] and val > 1) else val
    return val
def qty_137_(val,n):
    if val !=0:
        val =1
    return val
def stt_(v,n):
    try:
        v = int(v)
        return v
    except :
        return False
def tinh_trang_(v,n):
    if v ==None or v ==u'Tốt' or v==u'tot' or v ==False:
        return u'tot'
    else:
        return u'hong'
def ghi_chu_cho_sml_(v,n,self):
    if getattr(self, 'allow_cate_for_ghi_chu',False):
        return n.get('cate',False)#n['cate']#
    else:
        return v
# def name_replace_(v,n,self):
#     v = n['vof_dict']['prod_lot_id']['fields']['pn_id']['fields']['name']['val'] 
#     print ('val****',v)
#     if isinstance(v,str):
#         v = re.sub('[-_ \s]','',v)
#     return v
# def ghi_chu_cho_sml_cate_all_key_tram_(v,n,self):
#     if True:#getattr(self, 'allow_cate_for_ghi_chu',False):
#         return n.get('cate',False)
#     else:
#         return False
    
    
def pn_replace_(v,n,self):
    v = n['vof_dict']['product_id']['fields']['pn']['val'] 
    if isinstance(v,str):
        v = pn_replace(v)
#         v = re.sub('[-_ \s]','',v)
    
    return v
def product_id_(v,n,self):
    if v==False:
        v = n['vof_dict']['product_id']
        v = v.get('val',False)
    return v
def break_condition_func_for_main_instance_(needdata):
    needdata ['cate'] = needdata['vof_dict']['product_id_name_readonly']['val']
def tracking_write_func_(**kargs):
#     searched_object = kargs['searched_object']
#     f_name =  kargs['f_name']
    val =  kargs['val']
    if val =='none':
        return 'continue'
# def location_id_sml_(self):
#     product_id = 
#     return self.location_id.id
def location_id_sml_2_(v,n,self):
    product_id = n['vof_dict']['product_id']['val']
    prod_lot_id = n['vof_dict']['prod_lot_id']['val']
    quants = self.env['stock.quant'].search([('product_id','=',product_id),('lot_id','=',prod_lot_id),('location_id','child_of',self.location_id.id),('quantity','>',0)])
    if quants:
        return quants.location_id.id
    else:
        return self.location_id.id
    

def prod_lot_id_excel_readonly_for_search_(v,n,self):
    prod_lot_id_excel_readonly_name = n['vof_dict']['prod_lot_id_excel_readonly']['val']
    if prod_lot_id_excel_readonly_name:
        prod_lot_id_excel_readonly_for_search = self.env['stock.production.lot'].search([('name','=',prod_lot_id_excel_readonly_name)])
        return prod_lot_id_excel_readonly_for_search
    else:
        return False
# def product_id_excel_readonly_for_search_(v,n,self):
#     product_id_name_readonly = n['vof_dict']['product_id_name_readonly']['val']
#     if product_id_name_readonly:
#         prod_lot_id_excel_readonly_for_search = self.env['product.product'].search([('name','=',product_id_name_readonly),('pn','=',False)])
#         if len(prod_lot_id_excel_readonly_for_search)==1:
#             return prod_lot_id_excel_readonly_for_search
#     return False
    
# def set_val_instead_loop_fields_(n,self):
#     prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
#     if prod_lot_id_excel_readonly_for_search:
#         product_id = prod_lot_id_excel_readonly_for_search.product_id
#         uom_id = product_id.uom_id.id
#         print ('***uom_id***',uom_id)
#         n['vof_dict']['product_id']['fields']['uom_id']['val'] = uom_id
#         return product_id.id
#     else:
#         return None
# def set_val_instead_loop_fields_prod_lot_id_(n,self):
#     prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
#     if prod_lot_id_excel_readonly_for_search:
# #         product_id = prod_lot_id_excel_readonly_for_search.product_id
# #         uom_id = product_id.uom_id.id
# #         print ('***uom_id***',uom_id)
# #         n['vof_dict']['product_id']['fields']['uom_id']['val'] = uom_id
#         return prod_lot_id_excel_readonly_for_search.id
#     else:
#         return None
def exist_val_before_loop_fields_func_pr_id_(n,self): 
    prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
    if prod_lot_id_excel_readonly_for_search:
#         not_create2 = True
        return prod_lot_id_excel_readonly_for_search.product_id
    else:
        return False
def exist_val_before_loop_fields_func_pr_id_2_(n,self):
    product_id_excel_readonly_for_search = n['vof_dict']['product_id_excel_readonly_for_search']['val']
    if product_id_excel_readonly_for_search:
#         not_create2 = True
        return product_id_excel_readonly_for_search
    else:
        return False
    
def exist_val_before_loop_fields_func_lot_id_(n,self): 
    prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
    if prod_lot_id_excel_readonly_for_search:
        return prod_lot_id_excel_readonly_for_search
    else:
        return False
    
    
    
def check_excel_obj_is_exist_func_(get_or_create,obj,exist_val):
    if not get_or_create:
        raise UserError(u'lot_id: %s đã có nhưng lại tạo product_id')
    else:
        if exist_val not in obj:
            raise UserError(u'search obj (%s,%s) != exist_val (%s,%s)'%(obj.name,obj.pn, exist_val.name,exist_val.pn))
# def check_exist_val_before_loop_fields_func(n,self,get_or_create):
#     if get_or_create:
#         raise UserError(u'product in excel khách với lot_id.product')
#     else:
#         prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
#         return prod_lot_id_excel_readonly_for_search.product_id.id
    
def product_uom_id_(v,n,self):
    pr_id = n['vof_dict']['product_id']['val']
    uom_id = self.env['product.product'].browse(pr_id ).uom_id.id
    print ('pr_id','uom_id',pr_id,uom_id)
    return uom_id
        
def product_id_name_(v,n,self):
    v= n['vof_dict']['product_id_name_readonly']['val']
    v = str(int(v)) if  isinstance(v, float) else v
    return v
def search_func_(model_dict,self,exist_val,setting):
#     exist_val = search_func_para.get('exist_val')
    cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat = setting['cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat']
    cho_phep_co_pn_cap_nhat_empty_pn = setting['cho_phep_co_pn_cap_nhat_empty_pn']
#     print ('**model_dict',model_dict)
    name =  model_dict['fields']['name']['val']
    pn_replace = model_dict['fields']['pn_replace']['val']
    if not pn_replace:
        if exist_val:
            pr = self.env['product.product'].search([('name','=',name)])
            return pr
        else:
            pr = self.env['product.product'].search([('name','=',name),('pn','=',False)])
            if pr:
                return pr
            if cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat:
                pr = self.env['product.product'].search([('name','=',name)])
                if len(pr)==1 :
                    return pr
        return False
    else:
        pr = self.env['product.product'].search([('pn_replace','=',pn_replace)])
        if pr:
            return pr
        if cho_phep_co_pn_cap_nhat_empty_pn:
            pr = self.env['product.product'].search([('name','=',name),('pn','=',False)])
            if pr:
                return pr
        return False
    
        
        
        
#     print ('**model_dict name',)
#     print ('**model_dict name',)
#     if pn_replace:
#     pr = self.env['product.product'].search([('name','=',name),('pn','=',False)])
#     if pr:
#         return pr
#     if not pn_replace:
#         pr = self.env['product.product'].search([('name','=',name)])
#         if len(pr)==1:
#             return pr
        
        
def location_id5_chua_ro_(v,needdata,self):    
    v_all = needdata['vof_dict']['location_id5']['val'] \
                or needdata['vof_dict']['location_id4']['val'] or \
                needdata['vof_dict']['location_id3']['val'] or \
                needdata['vof_dict']['location_id2']['val'] or \
                needdata['vof_dict']['location_id1']['val']
    if  v_all ==False:
        return u'Chưa rõ'
    else:
        return False
def gen_model_dict(sml_title_row = False,self=None):                
    ALL_MODELS_DICT = {
     u'stock.inventory.line.tong.hop.ltk.dp.tti.dp': { #tong hop
                    'key_allow':True,
                    'largest_map_row_choosing':{sml:True,all_key_tram:False},                      
                    'title_rows':{
                        'key_ltk':[4,5],
                        'key_tti':[3,4],
                        key_ltk_dc:[0],
                        key_tti_dc:[0,1],
                        key_ltk_dc2:[7,8],
                        sml:sml_title_row or [0],
                        key_137: range(0,10)
                        
                        },
                    'title_rows_some_sheets':{'key_ltk':{u'XFP, SFP các loại':[2,3]}},
                    'begin_data_row_offset_with_title_row' :{all_key_tram:1,
                                                             key_tti_dc:2},
                    'sheet_names':{
                        'key_ltk':lambda self: [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name],
                        'key_tti':lambda self: [u'CHUYỂN MẠCH',u'IP',u'TRUYỀN DẪN',u'GTGT',u'VÔ TUYẾN']if not self.sheet_name else [self.sheet_name],
                        'key_ltk_dc':lambda self:[u'Tổng hợp']if not self.sheet_name else [self.sheet_name],
                        key_tti_dc:lambda self:[u'TTI-TS co'],
                        sml:lambda self,wb: [wb.sheet_names()[0]],
                        key_137:lambda self,wb: [ i for i in wb.sheet_names() if u'000' not in i],#[wb.sheet_names()[0]]
#                         key_137:lambda self,wb: [wb.sheet_names()[0]]
                        key_ltk_dc2:lambda self,wb: [wb.sheet_names()[0]],
                                   } ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                    'model':{all_key_tram: 'stock.inventory.line',sml:'stock.move.line'},## viet lai ben tao_instance_new
                   
                    'not_update_field_if_instance_exist_default':False,
                    'bypass_this_field_if_value_equal_False_default':False,
#                     'write_when_val_exist':True,
#                     'allow_check_excel_obj_is_exist_func':True,
                    'setting': {all_key_tram: {
                                               'write_when_val_exist':getattr(self,'write_when_val_exist',True),
                                               'allow_check_excel_obj_is_exist_func':getattr(self,'allow_check_excel_obj_is_exist_func',True),
                                               'cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat':getattr(self,'cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat',True),
                                               'cho_phep_co_pn_cap_nhat_empty_pn':getattr(self,'cho_phep_co_pn_cap_nhat_empty_pn',True),
                                               'cho_phep_exist_val_before_loop_fields_func':getattr(self,'cho_phep_exist_val_before_loop_fields_func',False),
#                                                 'allow_check_excel_obj_is_exist_raise_or_break':'break',

                                               }},
                                                      
                    'setting2': {sml: {'allow_check_excel_obj_is_exist_raise_or_break':'break'},
                                     all_key_tram:{'allow_check_excel_obj_is_exist_raise_or_break':'raise'}
                                 },
                    
                    'last_import_function':{all_key_tram:last_import_function_,sml:None},
                    'last_record_function':{all_key_tram:gan_inventory_id_vao_needdata,
                                                    key_ltk_dc:last_record_function_ltk_vtdc_,
                                                    sml:None},
                    'break_condition_func_for_main_instance':{#all_key_tram:None,
                                                              all_key_tram:break_condition_func_for_main_instance_,
                                                              key_137:None,
#                                                               all_key_tram:None,
                                                              },
                    'fields' : [
                        #first
          
                    ('barcode_for_first_read',{'empty_val':[u'NA',u"'",u"`"],
                                               'skip_this_field':{key_ltk_dc:False,
                                                                         'all_key_tram':True},
                                               'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,'xl_title':[u'Barcode'],'for_excel_readonly' :True}),
                   
                    ('prod_lot_id_excel_readonly',{'empty_val':{'key_ltk':[u'N/C'],
                                                                        'key_tti':[u'N/C',u'N/a',u'n/a',u'N/A'],
                                                                        'key_ltk_dc':[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN'],
                                                                        all_key_tram:[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN',u'N/C',u'N/a',u'n/a',u'N/A'],
                                                                }, 'func':lambda val,needdata: int(val) if isinstance(val,float) else val,
                                                                'xl_title':{all_key_tram:[u'Seri Number',u'Số serial (S/N)',u'Serial Number',u'Serial',u'S/N',u'SERI',u'Số S/N',u'''SERI
S/N'''],
                                                                            key_tti_dc: None,},
                                                                'for_excel_readonly' :True,
                                                                'required':{key_137:True},
                                                                'col_index':{'all_key_tram':None,
                                                                             key_tti_dc:20,
                                                                    }
                                                                }),
                    
                    
                  ('prod_lot_id_excel_readonly_for_search',{'for_excel_readonly' :True,'func':prod_lot_id_excel_readonly_for_search_}   ),
                          
                   
#                    ('stt_readonly',{'for_excel_readonly' :True,
#                                             'func':stt_, 
#                                             'xl_title': {'key_ltk':u'STT new',
#                                                 'key_tti':u'STT',
#                                                 'key_ltk_dc':u'STT',
#                                                  key_tti_dc: [u'Stt',u'Stt '],
#                                                  sml:u'STT',
#                                                  key_137:[u'SỐ']
#                                                  },
#                                              'skip_this_field':{sml:True},
#                                              'skip_field_if_not_found_column_in_some_sheet':True ,
#                       }
#                     ), 
                  
                    ('product_id_name_readonly',{'for_excel_readonly' :True,
                                             'col_index':{all_key_tram:None,
                                                                        key_tti_dc:11,
                                                                  },
                                             'xl_title':{'key_ltk':[u'TÊN VẬT TƯ',u'Module quang'],
                                                                    'key_ltk_dc':[u'Loại card'],
                                                                    'key_tti':[u'TÊN VẬT TƯ'],
                                                                    sml:[u'TÊN VẬT TƯ',u'Tên Vật Tư',u'Danh mục hàng hóa',u'Tên – Qui cách hàng hóa'],
                                                                    key_137:[u'TÊN TIẾNG VIỆT',u'TÊN THIẾT BỊ',u'Tên vật tư'],
                                                                    key_ltk_dc2:[u'Tên tài sản'],
                                                                    key_tti_dc:u'''Tên
                                                                    
chi tiết
thiết bị
(card)'''
                                                                 },
                                             'empty_val':{'key_ltk':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000'],all_key_tram:None}
#                                                      'key':True,
})  ,
                  
                    
#                      ('product_id_excel_readonly_for_search',{'for_excel_readonly' :True,'func':product_id_excel_readonly_for_search_ }   ),
                     ('stt',{
#                         'func':lambda v,n:n['vof_dict']['stt_readonly']['val'],
                        'func':stt_, 
                        'xl_title': {'key_ltk':u'STT new',
                            'key_tti':u'STT',
                            'key_ltk_dc':u'STT',
                             key_tti_dc: [u'Stt',u'Stt '],
                             sml:u'STT',
                             key_137:[u'SỐ'],
                             key_ltk_dc2:u'STT'
                             },
                        'skip_this_field':{key_137:True,all_key_tram:getattr(self,'skip_stt',False)},
                        'skip_field_if_not_found_column_in_some_sheet':True ,
                        'key':{all_key_tram:True},
                        'required_force':{all_key_tram:True},
                        'required_not_create':False
                      }
                 ), # bỏ stt ở đây để dùng trong hàm break, function
                                
                                
                    ('product_id',{'string':u'Tên Vật tư',
                                   'print_write_dict_new':True,
                                   'search_func':search_func_,
                                   'offset_write_xl':{sml:1}, 
                                   'key':'Both',
                                   'required':{all_key_tram:True},
                                   'required_not_create':False,
                                   'func':{all_key_tram:None,
                                             key_137: product_id_,
                                           },
                                   'exist_val_before_loop_fields_func':exist_val_before_loop_fields_func_pr_id_,
                                   'check_excel_obj_is_exist_func':{all_key_tram:check_excel_obj_is_exist_func_},#,sml:None
                                   'fields':[
                                            ('pn',{
                                                'type_allow':[int,float],
                                                'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'empty_val':[u'NA',u'-',u'--'],
                                                'xl_title':[u'Part-Number',u'Part Number',u'Partnumber',u'Mã card (P/N)',u'Mã vật tư',u'''MÃ 
VẬT TƯ''',u'''MÃ 
Article Code'''],
#                                                 'bypass_this_field_if_value_equal_False':True,
                                                'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:None},
                                                'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
                                                   }
                                             ),
                                            ('pn_replace',{'type_allow':[int,float],
                                                           'func':pn_replace_, 
                                                           'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
#                                                             'key':lambda n: True if n['vof_dict']['product_id']['fields']['pn_replace']['val'] else False ,
                                                            'key':True,
                                                            'bypass_this_field_if_value_equal_False':True,
                                                             'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
                                                            }
                                             ),
                                            ('name',{
                                                     'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
                                                     'func': product_id_name_,
                                                     'key':False,
#                                                     'key':lambda n: False if n['vof_dict']['product_id']['fields']['pn_replace']['val'] else True ,
#                                                      'key':False,
                                                     'required':True,
                                                     'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
                                                                  }),
                                            ('type',{'set_val':'product'}),

                                            ('tracking',{'func':{all_key_tram:lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else 'none',
                                                                        key_ltk_dc:lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else 'none',
                                                                        key_137: lambda v,n:'serial'
                                                                 }, 
                                                            'write_func': tracking_write_func_,
                                                         }),
                                             
                                          
                                          

                                            ('categ_id',{'skip_this_field':{sml:True,all_key_tram:False},
#                                                          'bypass_this_field_if_value_equal_False':True,
                                                           'key':False,
                                                           'set_val':{
                                                                    key_137: lambda self: self.categ_id.id,
                                                                    key_ltk_dc2:1
                                                                    },
                                                'fields':[('name',{
                                                                        'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                        'replace_string':{all_key_tram:[(u'Chuyển Mạch (IMS, Di Động)',u'Chuyển mạch'),(u'IP (VN2, VNP)',u'IP')]},
                                                                        
                                                                        'func':{ all_key_tram:lambda val,needdata: needdata['sheet_name'],
                                                                                    'key_tti':categ_id_tti_convert_to_ltk_,
                                                                                    key_ltk_dc: lambda val,needdata: needdata['sheet_name'],
                                                                                    key_tti_dc: None,
                                                                                    sml:None,
                                                                                    key_137:None,
#                                                                                     key_ltk_dc2:lambda v,n:1,
                                                                                },
                                                                        'karg':{'key_tti':{'tram':'TTI'}},
                                                                        'key':True,
#                                                                         'required': {all_key_tram:True,key_137:False}},
                                                                        'required':{all_key_tram:True, 
                                                                                    },
                                                                        'xl_title':{all_key_tram:None,
                                                                                    key_tti_dc:[u'Phân hệ'],
                                                                                    sml:[u'Nhóm'],
                                                                                    key_137:None
                                                                            },
                                                                            
                                                                        }
                                                            )
                                                          ]
                                                         }
                                             ),
                                             
                                            ('brand_id',{'empty_val':[u'NA'],
                                                                'skip_this_field':{sml:True,key_137:True},
                                                                'bypass_this_field_if_value_equal_False':True,
                                                                'fields':[('name',{'func':lambda v,n: v.upper() if isinstance(v,str) else v,
                                                                                                'xl_title':{'key_ltk':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                'key_tti':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                key_ltk_dc :[u'Hãng sản xuất'],
                                                                                                                 },
                                                                                                 'key':True,
                                                                                                 'required': True}),
                                                                              ]}),
                                              ('thiet_bi_id',{
                                                'skip_this_field':{key_137:True,sml:True},
                                                'bypass_this_field_if_value_equal_False':True,
                                                'get_or_create_para':{'key_tti':{'not_update_field_if_instance_exist':True},
                                                                        },
                                                'fields':[('name',{
                                                                'func':{all_key_tram:lambda v,n: str(v) if isinstance(v,float) else v,
                                                                         key_137: lambda v,n:n['sheet_name'],
                                                                        },
#                                                                     'type_allow':[float],
                                                                   'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:None},
                                                                               'xl_title':{'key_ltk':u'Thiết bị',
                                                                                           'key_tti':u'Thiết bị',
                                                                                           key_ltk_dc:u'Tên hệ thống thiết bị',
                                                                                           sml:u'Thiết bị',
                                                                                           key_tti_dc:u'''Tên
thiết bị'''
                                                                                           }, 
                                                                               'key':True,'required': True}),
                                                            ('categ_id',{ #'skip_this_field':{key_ltk_dc2:True},
                                                                                'key':True,'func': lambda v,n:n['vof_dict']['product_id']['fields']['categ_id']['val']}
                                                             ),
                                                            ('brand_id',{
                                                                         'skip_this_field':{key_137:True},
                                                                         'key':False,
                                                                         'bypass_this_field_if_value_equal_False':True,
                                                                         'func': lambda v,n:n['vof_dict']['product_id']['fields']['brand_id']['val']}),                                                               
                                                          ]}), 
                                             
                                            
                                            ('uom_id',  {'bypass_this_field_if_value_equal_False':True, 'fields': [ #'func':uom_id_,'default':1,
                                                        ('name',{'set_val':{
                                                                            all_key_tram:None,
                                                                            key_ltk_dc:u'Cái',
                                                                            key_ltk_dc2:u'Cái',
                                                                            key_tti_dc:u'Cái'
                                                                            },
                                                                 'func':{all_key_tram:name_of_uom_id_,key_137: uom_id_137_},
                                                                     'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'},},
                                                                      'xl_title':{all_key_tram:[u'Đơn vị tính',u'ĐVT',u'Đơn vị'],key_ltk_dc2:None },
                                                                      'key':True,'required':True,
                                                                      'replace_string':{'key_ltk':[('Modunle','module'),('CARD','Card'),('module','Module')],
                                                                                                'key_tti':[('CARD','Card'),('module','Module'),(u'bộ',u'Bộ')]
                                                                                    },
                                                                  'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']
                                                                                                             }
                                                                  }),
                                                                 ('category_id', {'func': lambda n,v,self:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn vị')])[0].id
                                                                                            }
                                                                     ),
                                          
                                                                           ]
                                                                }
                                             ),
                                             # Vật tư dự phòng LTK
#                                             ('ghi_chu_cho_sml_ngay_nhap',{'func':lambda val,needdata: convert_float_to_ghi_chu_cho_sml_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
#                                                                   'xl_title':[u'Ngày nhập',u'Ngày nhận',u'Năm sử dụng'],'skip_field_if_not_found_column_in_some_sheet':True}),
#                                             ('ghi_chu_cho_sml_ngay_xuat',{'func':lambda val,needdata: convert_float_to_ghi_chu_cho_sml_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
#                                                                   'xl_title':u'Ngày xuất','skip_field_if_not_found_column_in_some_sheet':True}),
#                                             ('ghi_chu_cho_sml_ban_dau',{'func':lambda val,needdata: val if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
#                                                                 'xl_title':[u'Ghi chú',u'Ghi chú - Mô tả thêm',u'diễn giải'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                           
#                                             ('du_phong_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc' not in self.key_tram }),
#                                             ('dang_chay_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc'  in self.key_tram }),
#                                             ('tram_ltk_tao',{'skip_this_field':{sml:True},'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram), 'bypass_this_field_if_value_equal_False':True }),
#                                             ('tram_tti_tao',{'skip_this_field':{sml:True},'set_val': lambda self: (self.key_tram and 'tti' in self.key_tram), 'bypass_this_field_if_value_equal_False':True  }),



#                                             ('ghi_chu_cho_sml_cate',{'skip_this_field':{sml:True,all_key_tram:False},'func': {all_key_tram:ghi_chu_cho_sml_cate_all_key_tram_} }),
                                            
                                            ]
                                   }),  
               
                 ('product_qty', {
                                     'type_allow':[int,float],
                                     'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                     'transfer_name':{sml:'qty_done'},
                                     'func':{all_key_tram:qty_,
                                             key_137:qty_137_,
#                                              key_ltk_dc2:1,
                                             },
                                     'replace_val':{'key_ltk':{u'XFP, SFP các loại':[(False,1)]}},
                                     'set_val':{'all_key_tram':None,
                                                    'key_ltk_dc':1,
                                                    key_tti_dc:1,
                                                    key_ltk_dc2:1,
#                                                     key_137:1,
                                                },
                                     'xl_title':{'key_ltk':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                                   'key_tti':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                                   sml:[u'Số lượng',u'Số lượng',u'S/L',u'Tồn kho cuối kỳ'],
                                                   key_137:[u'CUỐI',u'TỒN',u'Số lượng',u'SL']
                                                 },
                                     'key':False,
                                     'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                                
                                
                   

                 ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True,
                                     'func':location_goc_,
                                     'raise_if_False':True, 'skip_this_field':{sml:True}
                                     }),  
                
                ('department_id_for_excel_readonly',{'skip_this_field':{sml:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'for_excel_readonly':True,'key':False, 'func':look_department_from_key_tram_}),
                ('inventory_id', {'fields':[
                                        ('name',{'func':choose_inventory_id_name, 'key':True,'required': True}),
                                        ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                        ,], 'skip_this_field':{sml:True}
                    }),
                ('location_id1',{'skip_this_field':{sml:True,key_137:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                              'col_index':{all_key_tram:None,
                                                                                                key_tti_dc:22,
                                                                                          },
                                                                         'xl_title':{'key_ltk':u'Phòng',
                                                                                     'key_tti':u'Phòng',
                                                                                      key_ltk_dc:[u'Vị trí lắp đặt'],
                                                                                      key_ltk_dc2:[u'Vị trí lắp đặt'],
                                                                                      key_tti_dc:[u'''Vị trí
đặt'''],
                                                                                     },
                                                                          'key':True,'required': True,'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                ('stock_type',{'set_val':'phong_may'}),
                                                                ]
                                                       }), 
                ('location_id2',{'skip_this_field':{sml:True,key_137:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Tủ/Kệ',u'Tủ'],
                                                                                            'key_tti':[u'Tủ/Kệ',u'Tủ'],
                                                                                             key_ltk_dc:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_ltk_dc2:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_tti_dc:None,
                                                                                         },
                                                                              'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
    #                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                      ('stock_type',{'set_val':'tu'}),
                                                                    
                                                                    ]
                                                           }),                                           
                ('location_id3',{'skip_this_field':{sml:True,key_137:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                        'key_tti':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                         key_ltk_dc:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                         key_ltk_dc2:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                         key_tti_dc:None},
                                                                          'key':True,'required': True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True }),
                                                                ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                ('stock_type',{'set_val':'shelf'}),
                                                                
                                                                ]
                                                       }),         
                ('location_id4',{'skip_this_field':{sml:True,key_137:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Số thùng'],
                                                                                        'key_tti':[u'Số thùng'],
                                                                                         key_ltk_dc:[u'Số thứ tự (trong shelf)'],
                                                                                         key_ltk_dc2:[u'Số thứ tự (trong shelf)'],
                                                                                         key_tti_dc:None,
                                                                                        },   
                                                                  'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                ('stock_type',{'set_val':'stt_trong_self'}),
                                                                ]
                                                       }),  
              ('location_id5',{'skip_this_field':{sml:True,key_137:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{
                                                            'func':convert_float_location_,
                                                            'xl_title':{'key_ltk':[u'Hộp'],
                                                                        'key_tti':[u'Hộp'],
                                                                        key_ltk_dc:[u'Khe (Slot)'],
                                                                        key_ltk_dc2:[u'Khe (Slot)'],
                                                                        key_tti_dc:None,
                                                                        },        
                                                            'key':True,'required': True,
                                                            'skip_field_if_not_found_column_in_some_sheet':True,
#                                                             'func':location_id5_chua_ro_,
                                                            }),
                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                    ('stock_type',{'set_val':'slot',
#                                                                     'func': lambda v,n,self: 'slot' if n['vof_dict']['location_id5']['fields']['name']['val'] != u'Chưa rõ' else False
                                                                   
                                                                   }),
                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                    ]
                                           }),     
                                
                                
                ('location_id6',{'skip_this_field':{sml:True,key_137:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{
#                                                             'func':convert_float_location_,
                                                            'xl_title':{all_key_tram:None,
                                                                        },        
                                                            'key':True,
                                                            'required': True,
                                                            'func':location_id5_chua_ro_,
                                                            }),
                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id5']['val']  or needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                     ('stock_type',{#'set_val':'slot',
#                                                                     'func': lambda v,n,self: 'slot' if n['vof_dict']['location_id5']['fields']['name']['val'] != u'Chưa rõ' else False
#                                                                    }),
                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                    ]
                                           }),   
                                
                                
                                                         
               
                ('location_dest_id',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'set_val':{sml:lambda self: self.location_dest_id.id}}),
                ('picking_id',{'required':True, 'key':True, 'set_val':{sml:lambda self:self.id},'skip_this_field':{sml:False,all_key_tram:True}}),
               
                ('product_uom_id',{'skip_this_field':{sml:False,all_key_tram:True}, 
                                   'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                   'required_not_create':{sml:False},
#                                         'func':lambda v,n,self:n['vof_dict']['product_id']['fields']['uom_id']['val'] 
                                    'func':product_uom_id_,
                                   }),

                ('tinh_trang',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'set_val': {all_key_tram:u'tot',  sml:None},'xl_title':  {all_key_tram:None,  sml:[u'T/T',u'Tình trạng']},
                                                               'skip_field_if_not_found_column_in_some_sheet':True,
                                                               'func':tinh_trang_}),
                ('ghi_chu',{'xl_title':u'ghi chú', 'skip_this_field_for_mode_no_create':{all_key_tram:False},'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'func': {'sml':ghi_chu_cho_sml_,all_key_tram:None},'skip_field_if_not_found_column_in_some_sheet':True }),
#                     ('ghi_chu_cho_sml_cate',{'skip_this_field':{sml:True,all_key_tram:False},'func': {all_key_tram:ghi_chu_cho_sml_cate_all_key_tram_} }),
               
                ('prod_lot_id', {
                                 'offset_write_xl':{sml:2},
                                 'required_force':{all_key_tram:False,key_137:True},
                                 'transfer_name':{sml:'lot_id'},'key':True,'string':u'Serial number',
                                 'exist_val_before_loop_fields_func':exist_val_before_loop_fields_func_lot_id_,
#                                      'set_val_instead_loop_fields':{sml:set_val_instead_loop_fields_prod_lot_id_},
                                 
                                  'fields':[
                                                ('name',{'type_allow':[int],'required':{all_key_tram:True,  sml+ '_not_create':False},
                                                         'required_not_create':False,
                                                         'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
                                                         'func':{all_key_tram:lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],
                                                                    key_ltk_dc:lot_name_key_ltk_dc_,
                                                                 },'key':True
                                                         }),
            #                                     ('pn',{'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)']}),
                                                ('barcode_sn',{'skip_this_field':{key_ltk_dc:False,all_key_tram:True},'func':lambda v,n:n['vof_dict']['barcode_for_first_read']['val'] ,'key':True}),
                                               
 
                                                ('id_ke_toan',{'skip_this_field':{key_ltk_dc2:False,all_key_tram:True}, 'key':False,'xl_title':[u'ID - Không sửa cột này']}),
                                                ('the_tai_san',{'skip_this_field':{key_ltk_dc2:False,all_key_tram:True}, 'key':False,'xl_title':[u'Số thẻ']}),
                                                ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],
                                                               'key': True,
                                                                'required':True }),
                                                ('tinh_trang',{'skip_this_field':{sml:True,all_key_tram:False},'set_val': {all_key_tram:u'tot',  sml:None},'xl_title':  {all_key_tram:None,  sml:[u'T/T',u'Tình trạng']},
                                                               'skip_field_if_not_found_column_in_some_sheet':True,
                                                               'func': tinh_trang_}),

                                                ('ghi_chu_ngay_nhap',{'skip_this_field':{all_key_tram:True,key_137:False},'xl_title':[u'NHẬP'],'skip_field_if_not_found_column_in_some_sheet':True,'func':lambda v,n: convert_float_to_ghi_chu_cho_sml_ngay_xuat(v)}),
                                                ('ghi_chu_ngay_xuat',{'skip_this_field':{all_key_tram:True,key_137:False},'xl_title':[u'XUẤT'],'skip_field_if_not_found_column_in_some_sheet':True,'func':lambda v,n: convert_float_to_ghi_chu_cho_sml_ngay_xuat(v)}),
                                      
                                      ]
                                  }),
            ('location_id', {'skip_this_field':{all_key_tram:False}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                'func':{
                'sml':location_id_sml_2_,
                key_137: lambda v,n:n['vof_dict']['location_id_goc']['val'],
                all_key_tram: lambda v,needdata:needdata['vof_dict']['location_id6']['val'] or   needdata['vof_dict']['location_id5']['val'] or  needdata['vof_dict']['location_id4']['val'] or \
                needdata['vof_dict']['location_id3']['val'] or \
                needdata['vof_dict']['location_id2']['val'] or \
                needdata['vof_dict']['location_id1']['val'] or \
                needdata['vof_dict']['location_id_goc']['val']}
                , 'key':False}),
                                                 ]
                    },#End stock.inventory.line'
    }                               
#     ALL_MODELS_DICT.update(gen_product_model_dict())
    ALL_MODELS_DICT.update(gen_user_department_model_dict())
    ALL_MODELS_DICT.update(gen_tvcv_model_dict())
    return ALL_MODELS_DICT
    