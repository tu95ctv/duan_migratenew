# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression

class StockLocation(models.Model):
    _inherit = 'stock.location'
    department_id =  fields.Many2one('hr.department')
    partner_id_of_stock_for_report =  fields.Many2one('res.partner',string=u'Phòng ban cho báo cáo')
    cho_phep_am =  fields.Boolean(default=True,string=u'Cho phép số lượng âm')
    cho_phep_khac_tram_chon =  fields.Boolean(string=u'Cho phép khác trạm chọn')
    is_kho_cha =  fields.Boolean(string=u'Kho Cha')
    
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         print ( 'self._context',self._context)
#         return super(StockLocation,self).name_search( name, args=args, operator=operator, limit=limit)
    
    def get_stock_location_name_for_report_(self):
#         return self.department_id.get_department_name_for_report_() or self.partner_id_of_stock_for_report.name or self.name
        return self.partner_id_of_stock_for_report.name
        
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        limit = 100
        location_id = self._context.get('d4_location_id')
        print ('location_id',location_id)
        product_id = self._context.get('product_id_d4')
        if location_id:
            location_id_object = self.env['stock.location'].browse([location_id])
            if location_id_object.usage == 'internal':
                def filter_lots(r):
                    print ('product_id',product_id, type(product_id),'r.id',r.id)
#                     return True
                    quants = self.env['stock.quant'].search([('location_id','=',r.id),('product_id','=',int(product_id)),('quantity','>',0)])
                    print ('location_id',location_id,'r.id',r.id,'quants',quants,'len(quants)',len(quants))
                    if len(quants) >0 :
                        return True
                    else:
                        return False
                if args ==None:
                    args = []
#                 domain = expression.AND([[('name',operator,name)],args])
                recs = self.search(['|', ('barcode', operator, name), ('complete_name', operator, name)] + args, limit=limit)
#                 locations = self.env["stock.location"].search(domain, limit=limit)
                recs = recs.filtered(filter_lots )
                return recs.name_get()
        return super(StockLocation, self).name_search( name, args=args, operator=operator, limit=limit)
    
    
    def name_get(self):
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            while location.location_id and location.usage != 'view':
                location = location.location_id
#                 if not name:
#                     raise UserError(_('You have to set a name for this location.'))
                name = str(location.name) + "/" + str(name)
            ret_list.append((orig_location.id, name))
        return ret_list