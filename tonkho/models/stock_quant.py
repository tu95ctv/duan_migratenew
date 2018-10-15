# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from  odoo.addons.dai_tgg.mytools import name_compute
# import datetime
# from odoo.addons.tonkho.controllers.controllers import  download_quants,download_product,download_quants_moi_cage_moi_sheet
# from odoo.addons.tonkho.models.dl_models.dl_model_quants import  download_quants
# from odoo.addons.tonkho.models.dl_models.dl_model_product import  download_product
# from odoo import _





# from lxml import etree


    
            
class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"
#     pn = fields.Char(related='lot_id.pn')
    pn_id = fields.Many2one('tonkho.pn',related='lot_id.pn_id')
    categ_id = fields.Many2one('product.category', related='product_id.categ_id',store=True,string=u'Nhóm')
    thiet_bi_id = fields.Many2one('tonkho.thietbi',related='product_id.thiet_bi_id', string = u'Thiết bị',store=True)
    brand_id = fields.Many2one('tonkho.brand',related='product_id.brand_id',string=u'Hãng sản xuất',store=True)
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
#         ('lot', 'By Lots'),
        ('none', 'No Tracking')], string=u"Có SN hay không", related='product_id.tracking',store=True)
#     department_id = fields.Many2one('hr.department',related='location_id.department_id',store=True,string=u"Phòng ban")
    stock_location_id_selection = fields.Selection('get_stock_for_selection_field_',store=False)
    tinh_trang = fields.Selection([('tot',u'Tốt'),('hong',u'Hỏng')],default='tot',related='lot_id.tinh_trang',store=True,string=u'Tình trạng')
    ghi_chu = fields.Text(string=u'Ghi chú',related='lot_id.ghi_chu')
    stt = fields.Integer()
    inventory_line_id = fields.Many2one('stock.inventory.line')
    


    @api.model
    def create(self, values):
        if 'update_inventory' in self._context:
            values.update(self._context['update_inventory'])
        res = super(Quant, self).create(values)
        return res
     
    def get_stock_for_selection_field_(self):
        locs = self.env['stock.location'].search([('is_kho_cha','=',True)])
        rs = list(map(lambda i:(i.name,i.name),locs))
        return rs

    @api.constrains('location_id','quantity')
    def not_allow_negative_qty(self):
        for r in self:
            if not r.location_id.cho_phep_am:
                if r.quantity < 0:
                    raise UserError ( u' Không cho phép tạo âm')
   
    # GHI ĐÈ CÁI XEM DỊCH CHUYỂN KHO, KHÔNG CẦN LỌC VỊ TRÍ KHO
    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [
            ('product_id', '=', self.product_id.id),
#             '|', ('location_id', '=', self.location_id.id),
#             ('location_dest_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            ('package_id', '=', self.package_id.id)]
        return action
    
    
    def name_get(self):
        res = []
        for r in self:
            adict=[
                                                                 ('product_id',{'pr':None,'func':lambda r: r.name}),
                                                                 ('lot_id',{'pr':None,'func':lambda r: r.name,'skip_if_False':False}),
                                                                 ('quantity',{'pr':None,'func':lambda val:'%s'%val,'skip_if_False':False}),
                                                               ]
            name = name_compute(r,adict,join_char = u' | ')
            res.append((r.id,name))
        return res
    
    
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        context = self._context or {}
        if context.get('kho_da_chon') !=None:
            choosed_list = context.get('kho_da_chon') [0][2]
            args +=[('id','not in',choosed_list)]
        recs = self.search(['|',('product_id', operator, name),('lot_id.name', operator, name)] + args, limit=limit)
        return recs.name_get()
    
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('kho_da_chon') !=None:
            choosed_list = context.get('kho_da_chon') [0][2]
            args +=[('id','not in',choosed_list)]
        return super(Quant, self).search(args, offset, limit, order, count=count)
    
    @api.constrains('quantity')
    def check_quantity(self):
        for quant in self:
            if float_compare(quant.quantity, 1, precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
                raise ValidationError(_('A serial number should only be linked to a single product. %s,%s,%s'%(quant.quantity,quant.product_id.name,quant.lot_id.name)))
