# -*- coding: utf-8 -*-
{
    'name': "dai_tgg",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        NDT update 2510,04/06
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_import','product','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/cvi.xml',
        'views/tvcv.xml',
        'views/ctr.xml',
        'views/importthuvien.xml',
        'views/config.xml',
        'views/comment.xml',
        'views/ghichucongviec.xml',
        'views/else.xml',
       # 'views/assets.xml',
      #  'views/print.xml',
     #   'views/ca_truc.xml',
        #'views/view_ada.xml',
        #'views/wizard.xml',
      #  'views/templates.xml',
       # 'demo/demo.xml',
        'data/data.xml',
        'security/trucca_security.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}