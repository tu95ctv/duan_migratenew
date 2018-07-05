# -*- coding: utf-8 -*-
{
    'name': "Tồn Kho",

    'summary': """
        Quản lý vật tư, điều chuyển, in biên bản bàn giao""",

    'description': """
        Quản lý vật tư 04/07/2018
    """,

    'author': "Nguyễn Đức Tứ",
    'website': "http://113.161.80.108:8069/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'quản lý vật tư',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','hr','dai_tgg'],#'dai_tgg',
    #'css': ['static/src/css/style.css'], 
    # always loaded
    'data': [
            'security/data.xml',
        'security/security.xml',
    'report/header.xml',
    'report/main.xml',
    'report/table.xml',
        'security/ir.model.access.csv',
#         'views/stock_pack_operation.xml',
#         'views/stock_picking.xml',
        'views/stock_quant.xml',
        'views/hr_department.xml',
      'views/stock_inventory.xml',
       'views/stock_location.xml',
       'views/stock_production_lot.xml',
       'views/product_template.xml',
        'views/stock_move_line.xml',
        'views/stock_picking11.xml',
        'views/delete_menu.xml',
        'views/xoakho.xml',
        'views/warehouse.xml',
        'views/mau_ly_do.xml',
#     'report/totrinh_report.xml',
#         'views/pn.xml',
    'views/product_product.xml',
    'views/setting.xml',
    

        
        
        #'views/assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}