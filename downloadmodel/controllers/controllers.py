# -*- coding: utf-8 -*-
from odoo import http

# class Downloadmodel(http.Controller):
#     @http.route('/downloadmodel/downloadmodel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/downloadmodel/downloadmodel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('downloadmodel.listing', {
#             'root': '/downloadmodel/downloadmodel',
#             'objects': http.request.env['downloadmodel.downloadmodel'].search([]),
#         })

#     @http.route('/downloadmodel/downloadmodel/objects/<model("downloadmodel.downloadmodel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('downloadmodel.object', {
#             'object': obj
#         })