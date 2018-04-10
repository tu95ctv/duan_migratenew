# -*- coding: utf-8 -*-
from odoo import http

# class Tonkho11(http.Controller):
#     @http.route('/tonkho11/tonkho11/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tonkho11/tonkho11/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tonkho11.listing', {
#             'root': '/tonkho11/tonkho11',
#             'objects': http.request.env['tonkho11.tonkho11'].search([]),
#         })

#     @http.route('/tonkho11/tonkho11/objects/<model("tonkho11.tonkho11"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tonkho11.object', {
#             'object': obj
#         })