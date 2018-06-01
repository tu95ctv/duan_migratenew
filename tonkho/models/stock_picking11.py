# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

def _select_nextval(cr, seq_name):
    cr.execute("SELECT nextval('%s')" % seq_name)
    return cr.fetchone()

class ToTrinh(models.Model):
    _name = 'totrinh'
    name = fields.Char(u'Về Việc',required=True)
    so_to_trinh = fields.Char()
    ngay_to_trinh = fields.Date()
    
class StockPicking(models.Model):
    _inherit = "stock.picking"
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['hr.department'].browse(self.default_get([ 'department_id']).get('department_id')).default_stock_location_id,
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    
    department_id = fields.Many2one('hr.department',default=lambda self:self.env.user.department_id, readonly=True, string=u'Đơn Vị', required=True)
    stt_bien_ban = fields.Integer(default=lambda self:self.env.user.department_id.sequence_id.number_next_actual,readonly=True,string=u'STT')
    source_member_ids = fields.Many2many('res.partner','source_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân Viên Giao')
    dest_member_ids = fields.Many2many('res.partner','dest_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân Viên Nhận')
    ban_giao_or_nghiem_thu = fields.Selection([(u'ban_giao',u'Bàn Giao'),(u'nghiem_thu',u'Nghiệm Thu'),(u'su_dung',u'Đưa Vào Sử Dụng'),(u'nhap_kho_vat_tu_loi',u'Nhập kho vật tư lỗi')],default=u'ban_giao',string=u'Bàn Giao Hay Nghiệm Thu')
    don_vi_nhan = fields.Char(compute='don_vi_nhan_',string=u'Đơn Vị Nhận')
    don_vi_giao = fields.Char(compute='don_vi_giao_',string=u'Đơn Vị Giao')
    data_file = fields.Binary(string='File Import')
    filename = fields.Char()
    name = fields.Char(
        'Reference',
        default=lambda self:self.default_name(),
        copy=False,  index=True,
#         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
        )
    
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    ly_do = fields.Text(u'Lý Do')#Tình trạng vật tư: Vật tư đang sử dụng lỗi, đem SVTECH bảo hành,
    so_ban_in = fields.Integer(u'Số Bản In',default=2)
    ben_giao_giu = fields.Integer(u'Bên Giao Giữ', default=1)
    ben_nhan_giu = fields.Integer(u'Bên Nhận Giữ',default=1)
    totrinh_id = fields.Many2one('totrinh', string=u'Tờ trình')
   
   
   
    def default_name(self):
        defaults = self.default_get([ 'department_id'])
        int_department_id  = defaults.get('department_id')
        int_department_id =  int_department_id or self.department_id.id
        if int_department_id:
            department_id = self.env['hr.department'].browse(int_department_id)
            number_next = self.env.user.department_id.sequence_id.number_next_actual
            name = department_id.name + '/' + '%s'%number_next
            return name
        else:
            raise UserError(u'Bạn phải chọn department_id cho user')
    @api.onchange('picking_type_id')
    def onchange_picking_type_New(self):
        if self.picking_type_id:
            default_stock_location_id = self.env.user.department_id.default_stock_location_id.id
            if self.picking_type_id.code in  [ 'internal']:
                self.location_id = default_stock_location_id
#                 self.location_dest_id = False
#                 return {
#                     'domain':{
#                         'location_id': [('usage','=',u'internal')],
#                         'location_dest_id': [('usage','=',u'internal')]
#                         }
#                     }
            elif self.picking_type_id.code in  [ 'outgoing']:
                self.location_id = default_stock_location_id
#                 self.location_dest_id = False
#                 return {
#                     'domain':{
#                         'location_id': [('usage','=',u'internal')],
# #                         'location_dest_id': [('usage','=','view')]                      
#                        }
#                     }
            elif self.picking_type_id.code == 'incoming':
#                 self.location_id = False
                self.location_dest_id = default_stock_location_id
#                 return {
#                     'domain':{
# #                         'location_id': [('usage','=','view')],                      
#                         'location_dest_id': [('usage','=',u'internal')]
#                        }
#                     }
                 
    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
#         internal_transfers = self.env['stock.picking.type'].search(['|',('name','=','Internal Transfers'),('name','=',u'Dịch chuyển nội bộ')])
#         if internal_transfers:
#             internal_transfer_id = internal_transfers[0].id
#             res['picking_type_id'] = internal_transfer_id
        kho_dai_hcms = self.env['stock.location'].search([('name','=',u'Kho Đài HCM')])
        if kho_dai_hcms:
            kho_dai_hcm_id = kho_dai_hcms[0].id
            res['location_dest_id'] = kho_dai_hcm_id
            
        
        return res
    
    @api.onchange('department_id','picking_type_id')
    def name_(self):
        if self.department_id and self.picking_type_id:
#             picking_type_id = self.picking_type_id
            department_id = self.department_id
            number_next = department_id.sequence_id.number_next_actual
#             name = department_id.name + '/' + picking_type_id.sequence_id.prefix.split('/')[1] + '/' + '%s'%number_next
            name = department_id.name +  '/' + '%s'%number_next
            self.name = name
    @api.multi
    def ghom_stock_move_lines(self):
        """Changes picking state to done by processing the Stock Moves of the Picking
        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        # TDE FIXME: draft -> automatically done, if waiting ?? CLEAR ME
        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id) 
                if moves: #could search move that needs it the most (that has some quantities left)
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                   })
                    ops.move_id = new_move.id
                    todo_moves |= new_move
                    
                    
    @api.model
    def create(self, vals):
        defaults = self.default_get([ 'department_id','picking_type_id'])
        picking_type_id = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id')))
        department_id = self.env['hr.department'].browse(vals.get('department_id', defaults.get('department_id')))
        number_next = _select_nextval(self._cr, 'ir_sequence_%03d' % department_id.sequence_id.id)[0]
        
#         name = department_id.name + '/' + picking_type_id.sequence_id.prefix.split('/')[1] + '/' + '%s'%number_next
        name = department_id.name +  '/' + '%s'%number_next
        
        vals['stt_bien_ban'] = number_next #department_id.sequence_id.next_by_id()
        vals['name'] = name
        return super(StockPicking, self).create(vals)
    
    
    
    
    @api.multi
    def xem_print(self):
        return {
             'type' : 'ir.actions.act_url',
                'url':'/report/html/tonkho.report_picking_dai_hcm/%s'%self.id,
             'target': 'new',
        }
        
    @api.multi
    def xem_print_pdf(self):
        return {
             'type' : 'ir.actions.act_url',
                'url':'/report/pdf/tonkho.report_picking_dai_hcm/%s'%self.id,
             'target': 'new',
        }
        
        
        
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
    

    
    