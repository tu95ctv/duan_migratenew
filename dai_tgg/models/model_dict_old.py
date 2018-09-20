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
    p_id = needdata['vof_dict']['product_id']['val']
    product_id = self.env['product.product'].browse(p_id)
    UBC  = 'use barcode '
    lot_name = needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or (needdata['vof_dict']['barcode_for_first_read']['val'] and  (UBC +' ' + needdata['vof_dict']['barcode_for_first_read']['val']))
    if lot_name== UBC:
        lot_name= lot_name + str(int(needdata['vof_dict']['stt']['val']))
    elif  (lot_name ==False and  product_id.tracking=='serial'):
        lot_name = 'unknown ' + product_id.name + '  ' + str(int(needdata['vof_dict']['stt']['val']) )
    return lot_name

def last_record_function_ltk_vtdc_(n):
    if n['vof_dict']['product_id']['get_or_create']== False:# nếu product_id được tạo mới là sai
        raise UserError(u'Product %s  phải được tạo từ trước'%n['vof_dict']['product_id']['fields']['name']['val'])
    last_record_function_all_(n)

def last_record_function_all_(n):
    print ("n['vof_dict']['inventory_id']['val']",n['vof_dict']['inventory_id']['val'])
    if n['vof_dict']['inventory_id']['val'] and  not n.get('inventory_id'):
        n['inventory_id'] = n['vof_dict']['inventory_id']['val']
def last_import_function_all_(n,self):
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
def choose_inventory_id_name(v,n,self):
    return self.import_location_id.name + '-' +  ','.join(n['sheet_names'])
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
        val = int(val)
        val=  1 if  (n['vof_dict']['prod_lot_id_excel_readonly']['val'] and val > 1) else val
    return val


all_key_tram = 'all_key_tram'
key_ltk_dc = 'key_ltk_dc'
key_tti_dc = 'key_tti_dc'
from odoo.addons.dai_tgg.models.model_dict_product import gen_product_model_dict
from odoo.addons.dai_tgg.models.model_dict_user_department import gen_user_department_model_dict
def gen_model_dict():                
    ALL_MODELS_DICT = {
     u'stock.inventory.line.tong.hop.ltk.dp.tti.dp': { #tong hop
                    'key_allow':True,
                    'title_rows':{
                        'key_ltk':[4,5],
                        'key_tti':[3,4],
                        key_ltk_dc:[0],
                        key_tti_dc:[0,1]
                        },
                    'title_rows_some_sheets':{'key_ltk':{u'XFP, SFP các loại':[2,3]}},
                    'begin_data_row_offset_with_title_row' :{all_key_tram:1,
                                                             key_tti_dc:2},
                    'sheet_names':{
                        'key_ltk':lambda self: [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name],
                        'key_tti':lambda self: [u'CHUYỂN MẠCH',u'IP',u'TRUYỀN DẪN',u'GTGT',u'VÔ TUYẾN']if not self.sheet_name else [self.sheet_name],
                        'key_ltk_dc':lambda self:[u'Tổng hợp']if not self.sheet_name else [self.sheet_name],
                        key_tti_dc:lambda self:[u'TTI-TS co'],
                                   
                                   }  ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                    'model':'stock.inventory.line',
                    'last_import_function':last_import_function_all_,
                    'last_record_function':{all_key_tram:last_record_function_all_,
                                                    key_ltk_dc:last_record_function_ltk_vtdc_},
                    'fields' : [
                            ('stt',{'func':None, 'xl_title': {'key_ltk':u'STT new',
                                                                        'key_tti':u'STT',
                                                                        'key_ltk_dc':u'STT',
                                                                         key_tti_dc: [u'Stt',u'Stt ']
                                                              },'key':True, 'required':True,'skip_field_if_not_found_column_in_some_sheet':True}),
                         
                            
                            ('location_id_goc', {'model':'stock.location','key':False, 'for_excel_readonly' :True,"required":True, 
                                                 'set_val':lambda self: self.department_id.default_location_id.id,'raise_if_False':True}),  
                    ('barcode_for_first_read',{'empty_val':[u'NA',u"`"],
                                               'skip_this_field':{key_ltk_dc:False,
                                                                         'all_key_tram':True},
                                               'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,
                                               'xl_title':[u'Barcode'],
                                               'for_excel_readonly' :True,
                                               }),
                    ('prod_lot_id_excel_readonly',{'empty_val':{'key_ltk':[u'N/C'],
                                                                        'key_tti':[u'N/C',u'N/a',u'n/a',u'N/A'],
                                                                        'key_ltk_dc':[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN'],
                                                                        all_key_tram:[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN',u'N/C',u'N/a',u'n/a',u'N/A'],
                                                                }, 'func':lambda val,needdata: int(val) if isinstance(val,float) else val,
                                                                'xl_title':{all_key_tram:[u'Seri Number',u'Số serial (S/N)'],
                                                                            key_tti_dc: None,},
                                                                'for_excel_readonly' :True,
                                                                'col_index':{'all_key_tram':None,
                                                                             key_tti_dc:20,
                                                                    }
                                                                }),
                    
                    
                    ('product_qty', {'func':qty_,'replace_val':{'key_ltk':{u'XFP, SFP các loại':[(False,1)]}},
                                     'set_val':{'all_key_tram':None,
                                                    'key_ltk_dc':1,
                                                    key_tti_dc:1,
                                                },
                                     'xl_title':{'key_ltk':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                                   'key_tti':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ']
                                                 },
                                     'key':False,'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                    
                    ('inventory_id', {'fields':[
                                            ('name',{'func':choose_inventory_id_name, 'key':True,'required': True}),
                                            ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val']})
                                            ,]
                        }),
                    ('product_id',{'key':True,'required':True,
                                   'fields':[
                                            ('name',{'func':None,
                                                     'xl_title':{'key_ltk':[u'TÊN VẬT TƯ',u'Module quang'],
                                                                    'key_ltk_dc':[u'Loại card'],
                                                                    'key_tti':[u'TÊN VẬT TƯ'],
                                                                    key_tti_dc:u'''Tên
chi tiết
thiết bị
(card)'''
                                                                 },
                                                     'key':True,'required':True,
                                                     'empty_val':{'key_ltk':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000']}
                                                                  }),
                                            ('type',{'set_val':'product'}),
                                            
                                            ('tracking',{'func':{all_key_tram:lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else False,
                                                                        key_ltk_dc:lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else False,
                                                                 }, 
                                                         'bypass_this_field_if_value_equal_False':True}),
                                            
                                            ('thiet_bi_id',{
                                                'get_or_create_para':{'key_tti':{'not_update_field_if_instance_exist':True}},
                                                'fields':[('name',{'func':None,
                                                                               'xl_title':{'key_ltk':u'Thiết bị',
                                                                                           'key_tti':u'Thiết bị',
                                                                                           key_ltk_dc:u'Tên hệ thống thiết bị',
                                                                                           key_tti_dc:u'''Tên
thiết bị'''
                                                                                           }, 
                                                                               'key':True,'required': True}),]}),
                                          
                                            ('thiet_bi_id_tti',{'skip_this_field':{'key_ltk':True,
                                                                                                 key_ltk_dc:True,
                                                                                                 'key_tti':False,
                                                                                                 key_tti_dc:True
                                                                                                 },
                                                                    'fields':[('name',{'func':None,'xl_title':u'Thiết bị', 'key':True,'required': True}),]}),
                                             
                                            ('thiet_bi_id_ltk',{'skip_this_field':{'key_ltk':False,
                                                                                                 key_ltk_dc:False,
                                                                                                 'key_tti':True,
                                                                                                 key_tti_dc:True},
                                                                'fields':[('name',{'func':None,'xl_title':[u'Thiết bị',u'Tên hệ thống thiết bị'], 'key':True,'required': True}),]}),
                                             
                                            ('brand_id',{'empty_val':[u'NA'],
                                                                    'fields':[('name',{'func':lambda v,n: v.upper() if isinstance(v,str) else v,
                                                                                                'xl_title':{'key_ltk':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                'key_tti':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                key_ltk_dc :[u'Hãng sản xuất'],
                                                                                                            },
                                                                                                 'key':True,'required': True}),]}),
                                            ('categ_id',{
                                                'fields':[('name',{
                                                                        'func':{'all_key_tram':lambda val,needdata: needdata['sheet_name'],
                                                                                    'key_tti':categ_id_tti_convert_to_ltk_,
                                                                                    key_ltk_dc: None
                                                                                },
                                                                        'karg':{'key_tti':{'tram':'TTI'}},
                                                                        'key':True,
                                                                        'required': True,
                                                                        'xl_tilte':{all_key_tram:None,
                                                                                    key_tti_dc:[u'Phân hệ']
                                                                            }
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
                                                                      'xl_title':u'Đơn vị tính' ,'key':True,'required':True,
                                                                      'replace_string':{'key_ltk':[('Modunle','module'),('CARD','Card'),('module','Module')],
                                                                                                'key_tti':[('CARD','Card'),('module','Module'),(u'bộ',u'Bộ')]
                                                                                    },
                                                                  'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']
                                                                                                             }
                                                                  }),
                                                                 ('category_id', {'func': lambda n,v,self:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn Vị')])[0].id
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
                                                                'xl_title':[u'Ghi chú',u'Ghi chú - Mô tả thêm'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                           
                                            ('du_phong_tao',{'set_val':lambda self: 'dc' not in self.key_tram }),
                                            ('dang_chay_tao',{'set_val':lambda self: 'dc'  in self.key_tram }),
                                            ('tram_ltk_tao',{'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram), 'bypass_this_field_if_value_equal_False':True }),
                                            ('tram_tti_tao',{'set_val': lambda self: (self.key_tram and 'tti' in self.key_tram), 'bypass_this_field_if_value_equal_False':True  }),
                                            ]
                                   }),  
                    ('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':u'Phòng',
                                                                                         'key_tti':u'Phòng',
                                                                                          key_ltk_dc:[u'Vị trí lắp đặt'],
                                                                                          key_tti_dc:[u'''Vị trí
lắp
đặt'''],
                                                                                         },
                                                                              'key':True,'required': True,'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                     ('stock_type',{'set_val':'phong_may'}),
                                                                    ]
                                                           }), 
                    ('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Tủ/Kệ',u'Tủ'],
                                                                                            'key_tti':[u'Tủ/Kệ',u'Tủ'],
                                                                                             key_ltk_dc:[u'Tên tủ (Cabinet / rack)'],
                                                                                             key_tti_dc:None,
                                                                                         },
                                                                              'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
                                                                   ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                                     
                                                                      ('stock_type',{'set_val':'tu'}),
                                                                    
                                                                    ]
                                                           }),                                           
                    ('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                            'key_tti':[u'Ngăn',u'Ngăn/Kệ']},
                                                                                             key_ltk_dc:[u'Ngăn (shelf)'],
                                                                                             key_tti_dc:None,
                                                                              'key':True,'required': True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True }),
                                                                    ('stock_type',{'set_val':'shelf'}),
                                                                    
                                                                    ]
                                                           }),         
                    ('location_id4',{'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Số thùng'],
                                                                                            'key_tti':[u'Số thùng'],
                                                                                             key_ltk_dc:[u'Số thứ tự (trong shelf)'],
                                                                                             key_tti_dc:None,
                                                                                            },   
                                                                      'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                    ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                    ('stock_type',{'set_val':'stt_trong_self'}),
                                                                    ]
                                                           }),  
                  ('location_id5',{'model':'stock.location', 'for_excel_readonly':True,
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
                                                        ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                        ]
                                               }),                              
                    ('location_id', {'func':lambda v,needdata: needdata['vof_dict']['location_id4']['val'] or \
                        needdata['vof_dict']['location_id3']['val'] or \
                        needdata['vof_dict']['location_id2']['val'] or \
                        needdata['vof_dict']['location_id1']['val'] or \
                        needdata['vof_dict']['location_id_goc']['val']
                        , 'key':True}),
                    ('prod_lot_id', {'key':True,
                                      'fields':[
                                        ('name',{'func':lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],'key':True,'required':True}),
                                        ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],'key': True }),
    #                                     ('pn',{'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)']}),
                                        ('pn_id',{'model':'tonkho.pn',
                                                                      'fields':[
                                                                                ('name',{'empty_val':[u'NA',u'-',u'--'],'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)'],'key':True, 'required':True}),
                                                                                ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'] , 'key':True  }),
                                                                                ('import_location_id',{'set_val':lambda self: self.import_location_id.id}),
                                                                                ('du_phong_tao',{'set_val':lambda self: 'dc' not in self.key_tram}),
                                                                                ('tram_ltk_tao',{'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram)}),
    #                                                                             ('tram_tti_tao',{'set_val': (r.key_tram and 'tti' in r.key_tram)}),
                                                                                ]
                                                                      }),
                                        ('tinh_trang',{'set_val':u'tot'}),
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
    return ALL_MODELS_DICT
    