# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

def _select_nextval(cr, seq_name):
    cr.execute("SELECT nextval('%s')" % seq_name)
    return cr.fetchone()

class StockPicking(models.Model):
    _inherit = "stock.picking"
    department_id = fields.Many2one('hr.department',default=lambda self:self.env.user.department_id, readonly=True, string=u'Đơn Vị')
    stt_bien_ban = fields.Integer(default=lambda self:self.env.user.department_id.sequence_id.number_next_actual,readonly=True)
    don_vi_reference = fields.Char(readonly=True)
    source_member_ids = fields.Many2many('res.partner','source_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân Viên Giao')
    dest_member_ids = fields.Many2many('res.partner','dest_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân Viên Nhận')
    ban_giao_or_nghiem_thu = fields.Selection([(u'ban_giao',u'Bàn Giao'),(u'nghiem_thu',u'Nghiệm Thu'),(u'su_dung',u'Đưa Vào Sử Dụng'),(u'nhap_kho_vat_tu_loi',u'Nhập kho vật tư lỗi')],default=u'ban_giao',string=u'Bàn Giao Hay Nghiệm Thu')
    don_vi_nhan = fields.Char(compute='don_vi_nhan_',string=u'Đơn Vị Nhận')
    don_vi_giao = fields.Char(compute='don_vi_giao_',string=u'Đơn Vị Giao')
    pack_operation_product_ids = fields.One2many(
        'stock.pack.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        )
    ly_do = fields.Text(u'Lý Do')#Tình trạng vật tư: Vật tư đang sử dụng lỗi, đem SVTECH bảo hành,
    so_ban_in = fields.Integer(u'Số Bản In',default=2)
    ben_giao_giu = fields.Integer(u'Bên Giao Giữ', default=1)
    ben_nhan_giu = fields.Integer(u'Bên Nhận Giữ',default=1)
    totrinh_id = fields.Many2one('totrinh', string=u'Tờ trình')
    
    @api.onchange('picking_type_id')
    def onchange_picking_type_New(self):
        if self.picking_type_id:
            location_id = self.env.user.department_id.default_stock_location_id.id
            if self.picking_type_id.code in  [ 'outgoing', 'internal']:
                self.location_id = location_id
            elif self.picking_type_id.code == 'incoming':
                self.location_dest_id = location_id
                
    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        internal_transfers = self.env['stock.picking.type'].search([('name','=','Internal Transfers')])[0].id
        res['picking_type_id'] = internal_transfers
        return res
    
    
    def ban_giao_or_nghiem_thu_show(self):
        adict = {u'ban_giao':u'Bàn Giao',u'nghiem_thu':u'Nghiệm Thu'}
        if self.ban_giao_or_nghiem_thu != False:
            return adict[self.ban_giao_or_nghiem_thu]
        else:
            return False
    def don_vi_nhan_(self):
        self.don_vi_nhan = self.location_dest_id.partner_id.name if self.location_dest_id.partner_id.name else self.location_dest_id.name
    def don_vi_giao_(self):
        self.don_vi_giao = self.location_id.partner_id.name if self.location_id.partner_id.name else self.location_id.name
    @api.multi
    def write(self,vals):
        pack_operation_product_ids = vals.get('pack_operation_product_ids')
        if pack_operation_product_ids:
            check_list = any(map(lambda i:i[0]==0,pack_operation_product_ids))
            if check_list:#'pack_operation_product_ids' in vals:
                raise UserError(u'Ban khong duoc sua fields pack_operation_product_ids')
        res = super(StockPicking,self).write(vals)
        return res
    def _create_lots_for_picking(self):
        Lot = self.env['stock.production.lot']
        for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
            if not pack_op_lot.lot_id:
                lot = Lot.create({'name': pack_op_lot.lot_name, 
                                  'product_id': pack_op_lot.operation_id.product_id.id,
                                  'pn':pack_op_lot.pn_for_create,
                                  })
                pack_op_lot.write({'lot_id': lot.id})
        self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()
        
    @api.onchange('picking_type_id','department_id')
    def onchange_don_vi_reference(self):
        self.don_vi_reference = self.department_id.name + '/' + self.picking_type_id.sequence_id.prefix.split('/')[1] + '/' + '%s'%self. department_id.sequence_id.number_next_actual
    
    @api.model
    def create(self, vals):
        defaults = self.default_get([ 'department_id','picking_type_id'])
        picking_type_id = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id')))
        department_id = self.env['hr.department'].browse(vals.get('department_id', defaults.get('department_id')))
        number_next = _select_nextval(self._cr, 'ir_sequence_%03d' % department_id.sequence_id.id)[0]
        don_vi_reference = department_id.name + '/' + picking_type_id.sequence_id.prefix.split('/')[1] + '/' + '%s'%number_next
        vals['don_vi_reference'] = don_vi_reference
        vals['stt_bien_ban'] = number_next #department_id.sequence_id.next_by_id()
        vals['name'] = don_vi_reference
        return super(StockPicking, self).create(vals)
    