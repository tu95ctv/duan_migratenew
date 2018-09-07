 # -*- coding: utf-8 -*-
from odoo.exceptions import UserError
import datetime
# from odoo.addons.dai_tgg.mytools import convert_float_to_ghi_chu_ngay_xuat,lot_name_
 
 


def gen_user_department_model_dict():
    user_model_dict = {
        u'Partner': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Partner'],
                'model':'res.partner',
                'fields' : [
                         ('stt',{'func':None,'xl_title':u'stt','key':False,'required':True,'for_excel_readonly':True}),
                         ('name',{'func':None,'xl_title':u'Tên','key':False,'required':True}),
                        ('parent_id',{
                            'fields':[
                                                ('name',{'xl_title':u'Đơn vị','key':True,'required':True}),
                                                ('company_type',{'key':False, 'required': False, 'set_val':'company'}),
                                                       ]
                                            }
                         ),
                                               ('phone',{'func':None,'xl_title':u'phone','key':False, 'func': lambda v,n: int(v) if isinstance(v,float) else v}),
                                               ( 'email',{'func':None,'xl_title':u'email','key':True ,'required':True}),
                                                
                                                ('job_id',{'key':False,'required':False,
                                       'fields':[
                                                ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân Viên' if v==False else v }),
                                                ]
                                       }),  
 
                      ]
                },            
        u'location partner': {
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Location Partner'],
                'model':'stock.location',
                'fields' : [
                         ('name',{'func':None,'xl_title':u'Name','key':True,'required':True}),
                         ('usage',{'set_val':'supplier'}),
                         ('cho_phep_khac_tram_chon',{'set_val':True}),
                         ('partner_id_of_stock_for_report',{'fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                                       ]
                                            }
                         ),
                      ]
                },#location partner
        u'Department': {
        'title_rows' : [1], 
        'begin_data_row_offset_with_title_row' :1,
        'sheet_names': [u'Công Ty'],
        'model':'hr.department',
        'fields' : [
                ('name',{'func':None,'xl_title':u'công ty','key':True,'required':True}),
                ('report_name',{'func':None,'xl_title':u'report_name','key':False,'required':False}),
                ('short_name',{'func':None,'xl_title':u'short_name','key':False,'required':False}),
                ('parent_id',{'fields':[('name',{'xl_title':u'parent_id','key':True,'required':True}),
                                               ]
                                    }
                 ),
                ('cong_ty_type',{'fields':[('name',{'xl_title':u'cong_ty_type','key':True,'required':True}),
                                               ]
                                    }
                 ),
                ('sequence_id',{'fields':[
                    ('name',{'xl_title':None,'func':lambda v,n:n['vof_dict']['name']['val'] ,'key':True,'required':True}),
                    ('sequence_id_bbbg',{'model':'ir.sequence', 'for_excel_readonly':True,
                                                    'fields':[('name',{'xl_title':None, 'func':lambda v,n:n['vof_dict']['name']['val']+',' +'BBBG','key':True})]
                                         }),
                    ('sequence_id_ttr',{'model':'ir.sequence', 'for_excel_readonly':True,
                                                    'fields':[('name',{'xl_title':None, 'func':lambda v,n:n['vof_dict']['name']['val']+',' +'TTR','key':True})]
                                         }),
                                               ]
                                    }
                 ),
                ('default_location_id',{'fields':[
                    ('name',{'xl_title':u'default_location_id','func':None,'key':True,'required':True}),
                    ('partner_id_of_stock_for_report',{'fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                               ]
                                    }),
                    ('is_kho_cha',{'set_val':True}),
                    ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                    ('stock_type',{'set_val':'tram'}),
                    ('department_id',
                         {'fields':[
                             ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                                    ]
                          }),
                    ('location_id',{'fields':[('name',{'xl_title':u'location_id','key':True,'required':True}),
                                                                          ]
                                                               }
                                            ),                                                                                
                                                                        ]
                                                            }
                 ),
                     
                ('default_location_running_id',{'model':'stock.location','fields':[
                    ('name',{'xl_title':u'default_location_id_running','func':None,'key':True,'required':True}),
                    ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                    ('is_kho_cha',{'set_val':True}),
                     ('stock_type',{'set_val':'tram'}),
                     ('partner_id_of_stock_for_report',{'model':'res.partner','fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                               ]
                                    }
                 ),
                ('department_id',
                 {'model':'hr.department','fields':[
                     ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                            ]
                  }),
                     
                    ('location_id',{'model':'stock.location', 'fields':[('name',{'xl_title':u'location_id','key':True,'required':True}),
                                                                          ]
                                                               }
                                            ),                                                                                
                                                                        ]
                                                            }
                 ),
                    ('partner_id',{'key':False,'required':False,
       'fields':[
                ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['name']['val']}),
                ('company_type',{'xl_title':None,  'key':False, 'required': False, 'set_val':'company'}),
                ('parent_id',{'key':False,'required':False,
       'fields':[
                ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['parent_id']['fields']['name']['val'] }),
                ('company_type',{'xl_title':None,  'key':False, 'required': False, 'set_val':'company'}),
                ]
       }),  
                 
                ]
       }),  
              ]
                },#End department
        u'User': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': ['Sheet1'],
                'model':'res.users',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Họ và Tên','key':True,'required':True}),
                         ( 'login',{'func':None,'xl_title':u'Địa chỉ email','key':True ,'required':True}),
                        ('password',{'func':None,'required':True,'set_val':'123456'}),
                         ('lang',{'set_val':'vi_VN'}),
                         ('phone',{'func':None,'xl_title':u'Số điện thoại','key':False}),
               ('cac_sep_ids',{'key':False,'required':False,
                'fields':[
                         ('login',{'xl_title':u'Cấp trên',  'key':True, 'required':True, 'is_x2m_field':True}),
  
                         ]
                }),  
                ('groups_id',{'key':False,'required':False,'skip_field_cause_first_import':lambda self:self.skip_field_cause_first_import,
                'fields':[
                         ('name',{'xl_title':u'groups_id',  'key':True, 'required': True,'is_x2m_field':True,'remove_all_or_just_add_one_x2m':False}),     
                          ]
                }),  
                         ('job_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân viên' if v==False else v }),
                        ]
               }),  
                    ('department_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Bộ Phận',  'key':True, 'required': True}),
 
                          
                        ]
               }),  
                                        
                    ('partner_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['name']['val']}),
                        ('email',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['login']['val']}),
                        ('department_id',{'xl_title':None,  'key':False, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['val']}),
                         ('parent_id',{'key':False,'required':False,
                'fields':[
                         ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['fields']['name']['val'] }),
                          
                         ]
                }),  
                         
                        ]
               }),  
                      ]
                },#End users'
                   }
    return user_model_dict
    

                