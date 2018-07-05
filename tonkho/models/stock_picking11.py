# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

def _select_nextval(cr, seq_name):
    cr.execute("SELECT nextval('%s')" % seq_name)
    return cr.fetchone()
class ToTrinh(models.Model):
    _name = 'tonkho.title_cac_ben'
    name = fields.Char(u'Title',required=True)
class StockPicking(models.Model):
    _inherit = "stock.picking"
#     cancel_mode = fields.Boolean(compute='action_cancel_show_')
    choosed_stock_quants_ids = fields.Many2many('stock.quant',compute='choosed_stock_quants_ids_',store=False)
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['hr.department'].browse(self.default_get([ 'department_id']).get('department_id')).default_location_id,
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    noi_ban_giao = fields.Many2one('res.partner',default= lambda self: self.env.user.department_id.partner_id, string=u'Nơi bàn giao')
    department_id = fields.Many2one('hr.department',default=lambda self:self.env.user.department_id, readonly=True, string=u'Đơn vị', required=True)
#     stt_bien_ban = fields.Integer(default=lambda self:self.env.user.department_id.sequence_id.number_next_actual,readonly=True, string=u'STT điều chuyển')
    source_member_ids = fields.Many2many('res.partner','source_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân viên giao')
    dest_member_ids = fields.Many2many('res.partner','dest_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân viên nhận')
    ban_giao_or_nghiem_thu = fields.Selection([(u'BBBG',u'Bàn giao'),(u'TRVT',u'Trình vật tư'),
                                               (u'BBNT',u'Nghiệm thu'),(u'BBSD',u'Đưa vào sử dụng'),
                                               (u'BBNK',u'Nhập kho vật tư lỗi'),
                                               (u'HUY',u'Hủy biên bản'),
                                               (u'TRA',u'Trả vật tư lại do nhằm'),
                                               ],default=u'BBBG',string=u'BG hay NT')
#     data_file = fields.Binary(string='File Import')
#     filename = fields.Char()
#     stt_trong_bien_ban_in = fields.Integer(default=lambda self:self.default_get([ 'stt_bien_ban']).get('stt_bien_ban'),string=u'STT trong biên bản')
    stt_trong_bien_ban_in = fields.Integer(string=u'STT trong biên bản')
    ma_bien_ban = fields.Char(string=u'Mã biên bản')#default=lambda self:self.default_get([ 'ban_giao_or_nghiem_thu']).get('ban_giao_or_nghiem_thu'),
    name = fields.Char(
        'Reference',
#         default=lambda self:self.default_name(),
        copy=False,  index=True,
#         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
        )
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},default= lambda self: self.env['stock.picking.type'].search(['|',('name','=',u'Dịch chuyển nội bộ'),('name','=','Internal Transfers')])[0].id)
    ly_do = fields.Text(u'Lý do')#Tình trạng vật tư: Vật tư đang sử dụng lỗi, đem SVTECH bảo hành,
    so_ban_in = fields.Integer(u'Số bản in',default=4)
    ben_giao_giu = fields.Integer(u'Bên giao giữ', default=3)
    ben_nhan_giu = fields.Integer(u'Bên nhận giữ',default=1)
    totrinh_id = fields.Many2one('dai_tgg.totrinh', string=u'Tờ trình')
    title_ben_thu_3 = fields.Many2one('tonkho.title_cac_ben',string=u'Tiêu đề bên thứ 3')
    ben_thu_3_ids = fields.Many2many('res.partner','ben_thu_3_stock_picking_relate','picking_id','partner_id',string=u'Bên thứ 3')
    title_ben_thu_4 = fields.Many2one('tonkho.title_cac_ben',string=u'Tiêu đề bên thứ 4')
    ben_thu_4_ids = fields.Many2many('res.partner','ben_thu_4_stock_picking_relate','picking_id','partner_id',string=u'Bên thứ 4')
    texttemplate_id = fields.Many2one('tonkho.texttemplate',string=u"Mẫu lý do",domain=[('field_context','=','tonkho.stock.picking.field.ly_do')])
    
    @api.onchange('ban_giao_or_nghiem_thu')
    def ma_bien_ban_(self):
        self.ma_bien_ban = self.ban_giao_or_nghiem_thu


#     def action_cancel_show_(self):
#         for r in self:
#             r.cancel_mode=self.env['ir.config_parameter'].sudo().get_param('tonkho.cancel_mode')
    @api.onchange('department_id','ban_giao_or_nghiem_thu')
    def stt_trong_bien_ban_in_(self):
        picking = self.env['stock.picking'].search([('department_id','=',self.department_id.id),
                                                    ('ban_giao_or_nghiem_thu','=',self.ban_giao_or_nghiem_thu),
                                                    ('stt_trong_bien_ban_in','!=', 0),
                                                    ],limit=1,order='id desc')
        if picking:
            stt_trong_bien_ban_in = picking.stt_trong_bien_ban_in + 1
            self.stt_trong_bien_ban_in=stt_trong_bien_ban_in
        else:
            self.stt_trong_bien_ban_in = 1
    @api.onchange('texttemplate_id')
    def onchage_for_ly_do(self):
        self.ly_do = self.texttemplate_id.name
    # toi 07/06
#     is_locked = fields.Boolean(default=False, help='When the picking is not done this allows changing the '
#                                'initial demand. When the picking is done this allows '
#                                'changing the done quantities.')
    def generate_partner_bootstrap_ti_le(self):
        alist = []
        alist.append((u'Bên giao',self.source_member_ids[0].name if self.source_member_ids else ''))
        if self.ben_thu_3_ids:
            alist.append((self.title_ben_thu_3.name,self.ben_thu_3_ids[0].name))
        alist.append((u'Bên nhận',self.dest_member_ids[0].name if self.dest_member_ids else ''))
        if self.ben_thu_4_ids:
            alist.append((self.title_ben_thu_4.name, self.ben_thu_4_ids[0].name))
        return alist
   
    @api.depends('move_line_ids.stock_quant_id')
    def choosed_stock_quants_ids_(self):
        for r in self:
            r.choosed_stock_quants_ids =  r.move_line_ids.mapped('stock_quant_id')
        
    @api.multi
    @api.depends('state', 'move_lines')
    def _compute_show_mark_as_todo(self):
        for picking in self:
            if picking.state == 'done' or picking.state == 'confirmed'  :
                picking.show_mark_as_todo = False
            else:
                picking.show_mark_as_todo = True
# #             picking.show_mark_as_todo = True
# #             if not picking.move_lines:
# #                 picking.show_mark_as_todo = False
# #             if self._context.get('planned_picking') and picking.state == 'draft':
# #                 picking.show_mark_as_todo = True
# #             elif picking.state != 'draft' and picking.state != 'cancel' :# or not picking.id
# #                 picking.show_mark_as_todo = False
# #             else:
# #                 picking.show_mark_as_todo = True
                
# Tự làm tự bỏ    
#     def action_draft(self):
#         self.state = 'draft'
   
   
# default_name củ  
#     def default_name(self):
#         defaults = self.default_get([ 'department_id'])
#         int_department_id  = defaults.get('department_id')
#         int_department_id =  int_department_id or self.department_id.id
#         if int_department_id:
#             department_id = self.env['hr.department'].browse(int_department_id)
#             number_next = self.env.user.department_id.sequence_id.number_next_actual
#             name = department_id.short_name + '/' + '%s'%number_next
#             return name
#         else:
#             raise UserError(u'Bạn phải chọn department_id cho user')
    @api.onchange('department_id','ban_giao_or_nghiem_thu','stt_trong_bien_ban_in')
    def name_(self):
        name = self.department_id.short_name + '/' + '%s'%self.ban_giao_or_nghiem_thu + '/%s'%self.stt_trong_bien_ban_in
        self.name = name
          
        
        
    @api.onchange('picking_type_id')
    def onchange_picking_type_New(self):
        if self.picking_type_id:
            default_location_id = self.env.user.department_id.default_location_id.id
            if self.picking_type_id.code in  [ 'internal']:
                self.location_id = default_location_id
                self.location_dest_id = default_location_id
#                 self.location_dest_id = False
#                 return {
#                     'domain':{
#                         'location_id': [('usage','=',u'internal')],
#                         'location_dest_id': [('usage','=',u'internal')]
#                         }
#                     }
            elif self.picking_type_id.code in  [ 'outgoing']:
                self.location_id = default_location_id
#                 self.location_dest_id = False
#                 return {
#                     'domain':{
#                         'location_id': [('usage','=',u'internal')],
# #                         'location_dest_id': [('usage','=','view')]                      
#                        }
#                     }
            elif self.picking_type_id.code == 'incoming':
#                 self.location_id = False
                self.location_dest_id = default_location_id
#                 return {
#                     'domain':{
# #                         'location_id': [('usage','=','view')],                      
#                         'location_dest_id': [('usage','=',u'internal')]
#                        }
#                     }
                 
    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        kho_dai_hcms = self.env['stock.location'].search([('name','=',u'Kho Đài HCM')])
        if kho_dai_hcms:
            kho_dai_hcm_id = kho_dai_hcms[0].id
            res['location_dest_id'] = kho_dai_hcm_id
        return res
    

    
    @api.multi
    def action_confirm(self):
        self.ghom_stock_move_lines()
        # call `_action_confirm` on every draft move
        self.mapped('move_lines')\
            .filtered(lambda move: move.state == 'draft' or move.state == 'cancel')\
            ._action_confirm()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
            .mapped('move_lines')._action_assign()
        if self.env.context.get('planned_picking') and len(self) == 1:
            action = self.env.ref('stock.action_picking_form')
            result = action.read()[0]
            result['res_id'] = self.id
            result['context'] = {
                'search_default_picking_type_id': [self.picking_type_id.id],
                'default_picking_type_id': self.picking_type_id.id,
                'contact_display': 'partner_address',
                'planned_picking': False,
            }
            return result
        else:
            return True
        
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

#     Củ có number_next
#     @api.model
#     def create(self, vals):
#         defaults = self.default_get([ 'department_id','picking_type_id'])
#         department_id = self.env['hr.department'].browse(vals.get('department_id', defaults.get('department_id')))
#         number_next = _select_nextval(self._cr, 'ir_sequence_%03d' % department_id.sequence_id.id)[0]
#         name = department_id.short_name +  '/' + '%s'%number_next
#         vals['stt_bien_ban'] = number_next #department_id.sequence_id.next_by_id()
#         vals['name'] = name
#         return super(StockPicking, self).create(vals)
    
#     @api.model
#     def create(self, vals):
#         defaults = self.default_get([ 'department_id','picking_type_id'])
#         department_id = self.env['hr.department'].browse(vals.get('department_id', defaults.get('department_id')))
#        
#         number_next = _select_nextval(self._cr, 'ir_sequence_%03d' % department_id.sequence_id.id)[0]
#         name = department_id.short_name +  '/' + '%s'%number_next
#         vals['stt_bien_ban'] = number_next #department_id.sequence_id.next_by_id()
#         vals['name'] = name
#         return super(StockPicking, self).create(vals)
    
    
    
    @api.multi
    def xem_print(self):
        return {
             'type' : 'ir.actions.act_url',
             'url':'/report/html/tonkho.bao_cao_dieu_chuyen/%s'%self.id,
             'target': 'new',
        }
    @api.multi
    def xem_print_pdf(self):
        return {
            'type' : 'ir.actions.act_url',
            'url':'/report/pdf/tonkho.bao_cao_dieu_chuyen/%s'%self.id,
            'target': 'new',
        }
        
    def ban_giao_or_nghiem_thu_show(self):
        adict = {u'BBBG':u'Bàn Giao',u'BBNT':u'Nghiệm Thu'}
        if self.ban_giao_or_nghiem_thu != False:
            return adict[self.ban_giao_or_nghiem_thu]
        else:
            return False
#     @api.multi
#     def unlink(self):
#         for r in self:
#             mode_cancel = False
#             if mode_cancel and r.state !='cancel':
#                 raise UserError(u'Chỉ được xóa những biên bản có trạng thái Hủy')
#         return super(StockPicking, self).unlink()
    
    