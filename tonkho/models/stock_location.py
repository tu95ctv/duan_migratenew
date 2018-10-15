# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression
from odoo.addons.tonkho.tonkho_tool import  KHO_SELECTION, KHO_SELECTION_DICT

class StockLocation(models.Model):
    _inherit = 'stock.location'
    _rec_name = 'complete_name'
    department_id =  fields.Many2one('hr.department',string=u'Thuộc phòng ban')
    partner_id_of_stock_for_report =  fields.Many2one('res.partner',string=u'Phòng ban cho báo cáo')
    cho_phep_am =  fields.Boolean(default=True,string=u'Cho phép số lượng âm')
    cho_phep_khac_tram_chon =  fields.Boolean(string=u'Cho phép khác trạm chọn')
    is_kho_cha =  fields.Boolean(string=u'Kho cha')
    stock_type = fields.Selection(KHO_SELECTION
                                )
    
    
#     @api.one
#     @api.depends('name', 'location_id.complete_name','stock_type')
#     def _compute_complete_name(self):
#         """ Forms complete name of location from parent location to child location. """
#         if self.location_id.complete_name:
#             self.complete_name = '%s/%s' % (self.location_id.complete_name, self.get_name_with_type())
#         else:
#             self.complete_name = self.get_name_with_type()
            
            
    def get_name_with_type(self):
        if self.name:
            stock_type = KHO_SELECTION_DICT.get(self.stock_type)
            if stock_type:
                name = stock_type + ': '  + self.name 
                return name
        return self.name
     
    def name_get_1_record(self):
        location = self
        name = location.get_name_with_type()
        while location.location_id and location.usage != 'view':
            location = location.location_id
            if not name:
                raise UserError(_('You have to set a name for this location.'))
            name = location.get_name_with_type() + "/" + name
        return name
#     
    def name_get(self):
        ret_list = []
        show_loc_type = self._context.get('show_loc_type')
        for location in self:
            if  show_loc_type:
                name = location.name_get_1_record()
            else:
                name = location.complete_name
            ret_list.append((location.id, name))
        return ret_list
    
    
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         print ( 'self._context',self._context)
#         return super(StockLocation,self).name_search( name, args=args, operator=operator, limit=limit)
    def get_stock_location_name_for_report_(self):
        return self.partner_id_of_stock_for_report.name
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        limit = 100
        location_id = self._context.get('d4_location_id')
        product_id = self._context.get('product_id_d4')
        if location_id:
            location_id_object = self.env['stock.location'].browse([location_id])
            if location_id_object.usage == 'internal':
                def filter_lots(r):
                    quants = self.env['stock.quant'].search([('location_id','=',r.id),('product_id','=',int(product_id)),('quantity','>',0)])
                    if len(quants) >0 :
                        return True
                    else:
                        return False
                if args ==None:
                    args = []
                recs = self.search(['|', ('barcode', operator, name), ('complete_name', operator, name)] + args, limit=limit)
                recs = recs.filtered(filter_lots )
                return recs.name_get()
        return super(StockLocation, self).name_search( name, args=args, operator=operator, limit=limit)
    
#     def name_get(self):
#         ret_list = []
#         for location in self:
#             orig_location = location
#             name = location.name
#             while location.location_id and location.usage != 'view':
#                 location = location.location_id
# #                 if not name:
# #                     raise UserError(_('You have to set a name for this location.'))
#                 name = str(location.name) + "/" + str(name)
#             ret_list.append((orig_location.id, name))
#         return ret_list