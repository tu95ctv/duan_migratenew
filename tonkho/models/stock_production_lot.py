# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from odoo.osv import expression
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    pn = fields.Char(string=u'Part Number')
    ghi_chu = fields.Text(string=u'Ghi chú')
    ghi_chu_ban_dau =  fields.Text(string=u'Ghi chú ban đầu')
    ghi_chu_ngay_nhap = fields.Text(string=u'Ghi chú ngày nhập')
    ghi_chu_ngay_xuat = fields.Text(string=u'Ghi chú ngày xuất')
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        
        
        location_id = self._context.get('d4_location_id')
        print ('location_id',location_id)
        if location_id:
            location_id_object = self.env['stock.location'].browse([location_id])
            if location_id_object.usage == 'internal':
                def filter_lots(r):
                    quants = self.env['stock.quant'].search([('location_id','=',location_id),('lot_id','=',r.id),('quantity','>',0)])
                    print ('location_id',location_id,'r.id',r.id,'quants',quants,'len(quants)',len(quants))
                    if len(quants) >0 :
                        return True
                    else:
                        return False
                if args ==None:
                    args = []
                domain = expression.AND([[('name',operator,name)],args])
                lots = self.env["stock.production.lot"].search(domain, limit=limit)
                print  ('**lots 1',lots)
                lots = lots.filtered(filter_lots )
                print ('**lots 2',lots)
                return lots.name_get()
        return super(StockProductionLot,self).name_search( name, args=args, operator=operator, limit=limit)