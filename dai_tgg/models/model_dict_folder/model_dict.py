 # -*- coding: utf-8 -*-
 #Copy tu internal ham import _thu_vien
from odoo.exceptions import UserError
import datetime

# from odoo.addons.dai_tgg.models.model_dict_product import gen_product_model_dict
# from odoo.addons.dai_tgg.models.model_dict_user_department import gen_user_department_model_dict
# print ('***',type(product_model_dict))
# class self():
#     pass
def lot_name_(val,needdata,self):
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
    if not self.mode_not_create:
        if n['vof_dict']['product_id']['get_or_create']== False:# nếu product_id được tạo mới là sai
            raise UserError(u'Product %s  phải được tạo từ trước'%n['vof_dict']['product_id']['fields']['name']['val'])
    gan_inventory_id_vao_vof_dict_(n)
def gan_inventory_id_vao_vof_dict_(n):
    if n['vof_dict']['inventory_id']['val'] and  not n.get('inventory_id'):
        n['inventory_id'] = n['vof_dict']['inventory_id']['val']
def gan_inventory_id_(n,self):
    if not self.mode_not_create:
        self.inventory_id = n['inventory_id']
def convert_float_location_(v,n):
    if isinstance(v, float):
        v= str(int(v))
    return v
def convert_float_to_ghi_chu_ngay_xuat(val):
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
SHEET_CONVERT = {'TTI':{u'CHUYỂN MẠCH':u'Chuyển Mạch (IMS, Di Động)',u'IP':u'IP (VN2, VNP)',u'TRUYỀN DẪN':u'Truyền dẫn',u'GTGT': u'GTGT',u'VÔ TUYẾN' :u'Vô tuyến'}}
def categ_id_tti_convert_to_ltk_(v,n,tram=None):
#         raise UserError('kdkfasdlkfjld')
    v =  n['sheet_name']
    tram_dict = SHEET_CONVERT.get(tram)
    if tram_dict:
        return tram_dict.get(v,v)
    else:
        return v
    
###them self

def location_from_key_tram(v,n,self):
    key_tram = n['key_tram']
    key_tram_split = key_tram.split('_')
    tram = key_tram_split[1]
    if len(key_tram_split)>2:
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
        print ('val',val)
        val = float(int(val))
        val=  1.0 if  (n['vof_dict']['prod_lot_id_excel_readonly']['val'] and val > 1) else val
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
def ghi_chu_(v,n,self):
    if getattr(self, 'allow_cate_for_ghi_chu',False):
        return n.get('cate',False)
    else:
        return v
    
def ghi_chu_cate_all_key_tram_(v,n,self):
    if True:#getattr(self, 'allow_cate_for_ghi_chu',False):
        return n.get('cate',False)
    else:
        return False
    
    
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_product import gen_product_model_dict
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_user_department import gen_user_department_model_dict
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_tvcv import  gen_tvcv_model_dict

 
all_key_tram = 'all_key_tram'
key_ltk_dc = 'key_ltk_dc'
key_tti_dc = 'key_tti_dc'
write_xl = 'write_xl'
sml = 'sml'
key = 'key',
required = 'required'
product = 'key_tti_dc_product'
def break_condition_func_for_main_instance_(needdata):
    needdata ['cate'] = needdata['vof_dict']['product_id']['fields']['name']['val']
def tracking_write_func_(**kargs):
#     searched_object = kargs['searched_object']
#     f_name =  kargs['f_name']
    val =  kargs['val']
    if val =='none':
        return 'continue'
def gen_model_dict(sml_title_row = False,self=None):                
    ALL_MODELS_DICT = {
     u'stock.inventory.line.tong.hop.ltk.dp.tti.dp': { #tong hop
                    'key_allow':True,
                    'not_create':{
                                        all_key_tram: False,
                                        sml:True
                                  },
                                                      
                     'mode_not_create':{
                                        all_key_tram: self.mode_not_create,
                                        
                                  },                                 
                                                      
#                     'change_default':{{all_key_tram:False, product:True}},
                    
                    'largest_map_row_choosing':{sml:True,all_key_tram:False},                      
                    'title_rows':{
                        'key_ltk':[4,5],
                        'key_tti':[3,4],
                        key_ltk_dc:[0],
                        key_tti_dc:[0,1],
                        sml:sml_title_row or [0]
                        
                        },
                    'title_rows_some_sheets':{'key_ltk':{u'XFP, SFP các loại':[2,3]}},
                    'begin_data_row_offset_with_title_row' :{all_key_tram:1,
                                                             key_tti_dc:2},
                    'sheet_names':{
                        'key_ltk':lambda self: [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name],
                        'key_tti':lambda self: [u'CHUYỂN MẠCH',u'IP',u'TRUYỀN DẪN',u'GTGT',u'VÔ TUYẾN']if not self.sheet_name else [self.sheet_name],
                        'key_ltk_dc':lambda self:[u'Tổng hợp']if not self.sheet_name else [self.sheet_name],
                        key_tti_dc:lambda self:[u'TTI-TS co'],
                        sml:lambda self,wb: [wb.sheet_names()[0]]
                                   } ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                    'model':{all_key_tram: 'stock.inventory.line',sml:'stock.move.line'},## viet lai ben tao_instance_new
                    
                    'last_import_function':{all_key_tram:gan_inventory_id_,sml:None},
                    'last_record_function':{all_key_tram:gan_inventory_id_vao_vof_dict_,
                                                    key_ltk_dc:last_record_function_ltk_vtdc_,
                                                    sml:None},
                    'break_condition_func_for_main_instance':{#all_key_tram:None,
                                                              all_key_tram:break_condition_func_for_main_instance_,},
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
                                                                'xl_title':{all_key_tram:[u'Seri Number',u'Số serial (S/N)',u'Serial Number',u'Serial'],
                                                                            key_tti_dc: None,},
                                                                'for_excel_readonly' :True,
                                                                'col_index':{'all_key_tram':None,
                                                                             key_tti_dc:20,
                                                                    }
                                                                }),
                    
                    
                   
                    
                   
                   
                    
                    ('product_id',{'string':u'Tên Vật tư','offset_write_xl':{sml:1}, 'key':True,'required':{all_key_tram:True, sml+ '_not_create':False},'required_not_create':False,
                                   'fields':[
                                            ('name',{
                                                     'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
                                                     'func':None,
                                                     'col_index':{all_key_tram:None,
                                                                        key_tti_dc:11,
                                                                  },
                                                     'xl_title':{'key_ltk':[u'TÊN VẬT TƯ',u'Module quang'],
                                                                    'key_ltk_dc':[u'Loại card'],
                                                                    'key_tti':[u'TÊN VẬT TƯ'],
                                                                    sml:[u'TÊN VẬT TƯ',u'Tên Vật Tư',u'Danh mục hàng hóa',u'Tên – Qui cách hàng hóa'],
                                                                    key_tti_dc:u'''Tên
chi tiết
thiết bị
(card)'''
                                                                 },
                                                     'key':True,'required':True,
                                                     'empty_val':{'key_ltk':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000'],all_key_tram:None}
                                                                  }),
                                            ('type',{'set_val':'product'}),
#                                             ('tracking',{'func':{all_key_tram:lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else False,
#                                                                         key_ltk_dc:lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else False,
#                                                                  }, 
#                                                          'bypass_this_field_if_value_equal_False':True}),
                                            ('tracking',{'func':{all_key_tram:lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else 'none',
                                                                        key_ltk_dc:lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else 'none',
                                                                 }, 
#                                                          'bypass_this_field_if_value_equal_False':True
                                                            'write_func': tracking_write_func_,
                                                         }),
                                             
                                            ('thiet_bi_id',{
                                                'get_or_create_para':{'key_tti':{'not_update_field_if_instance_exist':True}},
                                                'fields':[('name',{
                                                                'func':lambda v,n: str(v) if isinstance(v,float) else v,
#                                                                     'type_allow':[float],
                                                                   'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:None},
                                                                               'xl_title':{'key_ltk':u'Thiết bị',
                                                                                           'key_tti':u'Thiết bị',
                                                                                           key_ltk_dc:u'Tên hệ thống thiết bị',
                                                                                           sml:u'Thiết bị',
                                                                                           key_tti_dc:u'''Tên
thiết bị'''
                                                                                           }, 
                                                                               'key':True,'required': True}),]}),
                                          
#                                             ('thiet_bi_id_tti',{'skip_this_field':{'key_ltk':True,
#                                                                                                  key_ltk_dc:True,
#                                                                                                  'key_tti':False,
#                                                                                                  key_tti_dc:True,
#                                                                                                  sml:True,
#                                                                                                  },
#                                                                     'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
#                                              
#                                             ('thiet_bi_id_ltk',{'skip_this_field':{'key_ltk':False,
#                                                                                                  key_ltk_dc:False,
#                                                                                                  'key_tti':True,
#                                                                                                  key_tti_dc:True,
#                                                                                                  sml:True},
#                                                                 'fields':[('name',{'func':None,'xl_title':[u'Thiết bị',u'Tên hệ thống thiết bị'], 'key':True,'required': True}),]}),
#                                              
                                          
                                            ('brand_id',{'empty_val':[u'NA'],'skip_this_field':{sml:True},
                                                                    'fields':[('name',{'func':lambda v,n: v.upper() if isinstance(v,str) else v,
                                                                                                'xl_title':{'key_ltk':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                'key_tti':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                key_ltk_dc :[u'Hãng sản xuất'],
                                                                                                                 },
                                                                                                
                                                                                                 'key':True,'required': True}),]}),
                                            ('categ_id',{'skip_this_field':{sml:True, all_key_tram:False},
                                                'fields':[('name',{
                                                                        
                                                                        'func':{all_key_tram:lambda val,needdata: needdata['sheet_name'],
                                                                                    'key_tti':categ_id_tti_convert_to_ltk_,
                                                                                    key_ltk_dc: lambda val,needdata: needdata['sheet_name'],
                                                                                    key_tti_dc: None
                                                                                },
                                                                        'karg':{'key_tti':{'tram':'TTI'}},
                                                                        'key':True,
                                                                        'required': True,
                                                                        'xl_title':{all_key_tram:None,
                                                                                    key_tti_dc:[u'Phân hệ']
                                                                            },
                                                                            
                                                                        }
                                                            )
                                                          ]
                                                         }
                                             ),
                                            ('uom_id',  {'bypass_this_field_if_value_equal_False':True, 'fields': [ #'func':uom_id_,'default':1,
                                                        ('name',{'set_val':{
                                                                            all_key_tram:None,
                                                                            key_ltk_dc:u'Cái',
                                                                            key_tti_dc:u'Cái'
                                                                            },'func':name_of_uom_id_,'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'},},
                                                                      'xl_title':[u'Đơn vị tính',u'ĐVT'] ,'key':True,'required':True,
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
                                            ('ghi_chu_ngay_nhap',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
                                                                  'xl_title':[u'Ngày nhập',u'Ngày nhận',u'Năm sử dụng'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                            ('ghi_chu_ngay_xuat',{'func':lambda val,needdata: convert_float_to_ghi_chu_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
                                                                  'xl_title':u'Ngày xuất','skip_field_if_not_found_column_in_some_sheet':True}),
                                            ('ghi_chu_ban_dau',{'func':lambda val,needdata: val if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
                                                                'xl_title':[u'Ghi chú',u'Ghi chú - Mô tả thêm',u'diễn giải'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                           
                                            ('du_phong_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc' not in self.key_tram }),
                                            ('dang_chay_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc'  in self.key_tram }),
                                            ('tram_ltk_tao',{'skip_this_field':{sml:True},'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram), 'bypass_this_field_if_value_equal_False':True }),
                                            ('tram_tti_tao',{'skip_this_field':{sml:True},'set_val': lambda self: (self.key_tram and 'tti' in self.key_tram), 'bypass_this_field_if_value_equal_False':True  }),
                                            ('ghi_chu_cate',{'skip_this_field':{sml:True,all_key_tram:False},'func': {all_key_tram:ghi_chu_cate_all_key_tram_} }),
                                            
                                            ]
                                   }),  
                ('stt',{'func':stt_, 'xl_title': {'key_ltk':u'STT new',
                                            'key_tti':u'STT',
                                            'key_ltk_dc':u'STT',
                                             key_tti_dc: [u'Stt',u'Stt '],
                                             sml:u'STT'
                                             },
                        'key':True, 'required':True,'skip_field_if_not_found_column_in_some_sheet':True ,
                      }
             ),
                                
                 ('product_qty', {
                                     'skip_this_field_2':{key_ltk_dc:True},
                                     'transfer_name':{sml:'qty_done'},
                                     'func':qty_,'replace_val':{'key_ltk':{u'XFP, SFP các loại':[(False,1)]}},
                                     'set_val':{'all_key_tram':None,
                                                    'key_ltk_dc':1,
                                                    key_tti_dc:1,
                                                },
                                     'xl_title':{'key_ltk':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                                   'key_tti':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                                   sml:[u'Số lượng',u'Số lượng',u'S/L']
                                                 },
                                     'key':False,'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                                
                                
                   
                ('pn_id',{ 'offset_write_xl':{sml:2},'model':'tonkho.pn','string':u'Mã vật tư',
                                                                  'fields':[
                                                                            ('name',{'type_allow':[int], 'empty_val':[u'NA',u'-',u'--'],'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)',u'Mã vật tư'],'key':True,
                                                                                     'required': True,'func':lambda val,needdata: int(val) if isinstance(val,float) else val
                                                                                     }),
                                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True, 'required':True   }),
#                                                                             ('import_location_id',{'skip_this_field':{sml:True},'set_val':lambda self: self.import_location_id.id}),
                                                                            ('du_phong_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc' not in self.key_tram}),
                                                                            ('tram_ltk_tao',{'skip_this_field':{sml:True},'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram)}),
                #                                                                             ('tram_tti_tao',{'set_val': (r.key_tram and 'tti' in r.key_tram)}),
                                                                            ]
                                                                  }),  
                 ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True,
                                     'func':location_goc_,
                                     'raise_if_False':True, 'skip_this_field':{sml:True}
                                     }),  
                ('department_id_for_excel_readonly',{'skip_this_field':{sml:True}, 'skip_this_field_2':{key_ltk_dc:True},'for_excel_readonly':True,'key':False, 'func':look_department_from_key_tram_}),
                ('inventory_id', {'fields':[
                                        ('name',{'func':choose_inventory_id_name, 'key':True,'required': True}),
                                        ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                        ,], 'skip_this_field':{sml:True}
                    }),
                                
                                
                    ('location_id1',{'skip_this_field':{sml:True}, 'skip_this_field_2':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True, 'skip_this_field_2':{key_ltk_dc:True},
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                                  'col_index':{all_key_tram:None,
                                                                                                    key_tti_dc:22,
                                                                                              },
                                                                             'xl_title':{'key_ltk':u'Phòng',
                                                                                         'key_tti':u'Phòng',
                                                                                          key_ltk_dc:[u'Vị trí lắp đặt'],
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
                    ('location_id2',{'skip_this_field':{sml:True}, 'skip_this_field_2':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Tủ/Kệ',u'Tủ'],
                                                                                            'key_tti':[u'Tủ/Kệ',u'Tủ'],
                                                                                             key_ltk_dc:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_tti_dc:None,
                                                                                         },
                                                                              'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
#                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                      ('stock_type',{'set_val':'tu'}),
                                                                    
                                                                    ]
                                                           }),                                           
                    ('location_id3',{'skip_this_field':{sml:True}, 'skip_this_field_2':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                            'key_tti':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                             key_ltk_dc:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                             key_tti_dc:None},
                                                                              'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True }),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                    ('stock_type',{'set_val':'shelf'}),
                                                                    
                                                                    ]
                                                           }),         
                    ('location_id4',{'skip_this_field':{sml:True}, 'skip_this_field_2':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Số thùng'],
                                                                                            'key_tti':[u'Số thùng'],
                                                                                             key_ltk_dc:[u'Số thứ tự (trong shelf)'],
                                                                                             key_tti_dc:None,
                                                                                            },   
                                                                      'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                    ('stock_type',{'set_val':'stt_trong_self'}),
                                                                    ]
                                                           }),  
                  ('location_id5',{'skip_this_field':{sml:True}, 'skip_this_field_2':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                               'fields':[
                                                        ('name',{'func':convert_float_location_,
                                                                'xl_title':{'key_ltk':[u'Hộp'],
                                                                            'key_tti':[u'Hộp'],
                                                                            key_ltk_dc:[u'Khe (Slot)'],
                                                                            key_tti_dc:None,
                                                                            },        
                                                                'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                        ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                        ('stock_type',{'set_val':'slot'}),
#                                                         ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                        ]
                                               }),                              
                    ('location_id', {'skip_this_field':{all_key_tram:False}, 'skip_this_field_2':{key_ltk_dc:True},
                        'set_val':{sml:lambda self:self.location_id.id},
                        'func':{'sml':None,
                        all_key_tram: lambda v,needdata: needdata['vof_dict']['location_id4']['val'] or \
                        needdata['vof_dict']['location_id3']['val'] or \
                        needdata['vof_dict']['location_id2']['val'] or \
                        needdata['vof_dict']['location_id1']['val'] or \
                        needdata['vof_dict']['location_id_goc']['val']}
                        , 'key':True}),
                    ('location_dest_id',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_2':{key_ltk_dc:True},'set_val':{sml:lambda self: self.location_dest_id.id}}),
                    ('picking_id',{'required':True, 'key':True, 'set_val':{sml:lambda self:self.id},'skip_this_field':{sml:False,all_key_tram:True}}),
                   
                    ('product_uom_id',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_2':{key_ltk_dc:True},'func':lambda v,n,self:n['vof_dict']['product_id']['fields']['uom_id']['val'] }),

                    ('tinh_trang',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_2':{key_ltk_dc:True},'set_val': {all_key_tram:u'tot',  sml:None},'xl_title':  {all_key_tram:None,  sml:[u'T/T',u'Tình trạng']},
                                                                   'skip_field_if_not_found_column_in_some_sheet':True,
                                                                   'func':tinh_trang_}),
                    ('ghi_chu',{'xl_title':u'ghi chú', 'skip_this_field_2':{all_key_tram:False},'skip_this_field_2':{key_ltk_dc:True},'func': {'sml':ghi_chu_,all_key_tram:None},'skip_field_if_not_found_column_in_some_sheet':True }),
#                     ('ghi_chu_cate',{'skip_this_field':{sml:True,all_key_tram:False},'func': {all_key_tram:ghi_chu_cate_all_key_tram_} }),
                    ('prod_lot_id', {'offset_write_xl':{sml:3},'transfer_name':{sml:'lot_id'},'key':True,'string':u'Serial number',
                                      'fields':[
                                                    ('name',{'type_allow':[int],'required':{all_key_tram:True,  sml+ '_not_create':False},'required_not_create':False,
                                                             'func':{all_key_tram:lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],
                                                                        key_ltk_dc:lot_name_,
                                                                     },'key':True
                                                             }),
                #                                     ('pn',{'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)']}),
                                                    ('barcode_sn',{'skip_this_field':{key_ltk_dc:False,all_key_tram:True},'func':lambda v,n:n['vof_dict']['barcode_for_first_read']['val'] ,'key':True}),
                                                    ('pn_id',{'model':'tonkho.pn','string':u'Mã vật tư',
                                                                  'fields':[
                                                                            ('name',{'type_allow':[int], 'empty_val':[u'NA',u'-',u'--'],'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)',u'Mã vật tư'],'key':True,
                                                                                     'required': True,'func':lambda val,needdata: int(val) if isinstance(val,float) else val
                                                                                     }),
                                                                            ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True, 'required':True   }),
#                                                                             ('import_location_id',{'skip_this_field':{sml:True},'set_val':lambda self: self.import_location_id.id}),
                                                                            ('du_phong_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc' not in self.key_tram}),
                                                                            ('tram_ltk_tao',{'skip_this_field':{sml:True},'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram)}),
                #                                                                             ('tram_tti_tao',{'set_val': (r.key_tram and 'tti' in r.key_tram)}),
                                                                            ]
                                                                  }),
                                                    ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],'key': True, 'required':True }),
                                                    ('tinh_trang',{'skip_this_field':{sml:True,all_key_tram:False},'set_val': {all_key_tram:u'tot',  sml:None},'xl_title':  {all_key_tram:None,  sml:[u'T/T',u'Tình trạng']},
                                                                   'skip_field_if_not_found_column_in_some_sheet':True,
                                                                   'func': tinh_trang_}),
                                                    ('ghi_chu_ngay_xuat',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_xuat']['before_func_val'])}),
                                                   #copy
                                                    ('ghi_chu_ngay_nhap',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ngay_nhap']['before_func_val'])}),
                                                    ('ghi_chu_ban_dau',{'func':lambda v,n: convert_float_to_ghi_chu_ngay_xuat(n['vof_dict']['product_id']['fields']['ghi_chu_ban_dau']['before_func_val'])}),
                                          
                                          ]
                                      }),
                                
                      
                                             ]
                    },#End stock.inventory.line'
    }                               
    ALL_MODELS_DICT.update(gen_product_model_dict())
    ALL_MODELS_DICT.update(gen_user_department_model_dict())
    ALL_MODELS_DICT.update(gen_tvcv_model_dict())
    return ALL_MODELS_DICT
    