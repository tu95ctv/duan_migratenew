# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from datetime import timedelta

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
    source_member_ids = fields.Many2many('res.partner','source_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân viên giao',copy=False)
    dest_member_ids = fields.Many2many('res.partner','dest_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân viên nhận',copy=False)
    ban_giao_or_nghiem_thu = fields.Selection([(u'BBBG',u'Bàn giao'),(u'TRVT',u'Trình vật tư'),
                                               (u'BBNT',u'Nghiệm thu'),(u'BBSD',u'Đưa vào sử dụng'),
                                               (u'BBNK',u'Nhập kho vật tư lỗi'),
                                               (u'HUY',u'Hủy biên bản'),
                                               (u'TRA',u'Trả vật tư lại do nhằm'),
                                               (u'TDTT',u'Thay đổi tình trạng vật tư'),
                                               (u'DCNB',u'Dịch chuyển nội bộ'),
                                               ],default=u'BBBG', string=u'B/giao hay N/thu',copy=False)
#     data_file = fields.Binary(string='File Import')
#     filename = fields.Char()
#     stt_trong_bien_ban_in = fields.Integer(default=lambda self:self.default_get([ 'stt_bien_ban']).get('stt_bien_ban'),string=u'STT trong biên bản')
    stt_trong_bien_ban_in = fields.Integer(string=u'STT trong biên bản',compute='stt_trong_bien_ban_in_',store=True,copy=False)
#     stt_trong_bien_ban_in = fields.Integer(string=u'STT trong biên bản',copy=False)
    ma_bien_ban = fields.Char(string=u'Mã biên bản',compute='ma_bien_ban_',store=True,copy=False)#default=lambda self:self.default_get([ 'ban_giao_or_nghiem_thu']).get('ban_giao_or_nghiem_thu'),
    name = fields.Char(
        compute='name_',store=True,
        string='Reference',
#         default=lambda self:self.default_name(),
        copy=False,  index=True,
#         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
        )
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},default= lambda self: self.env['stock.picking.type'].search(['|',('name','=',u'Dịch chuyển nội bộ'),('name','=','Internal Transfers')])[0].id)
    ly_do = fields.Text(u'Lý do',copy=False)#Tình trạng vật tư: Vật tư đang sử dụng lỗi, đem SVTECH bảo hành,
    so_ban_in = fields.Integer(u'Số bản in',default=4,copy=False)
    ben_giao_giu = fields.Integer(u'Bên giao giữ', default=3,copy=False)
    ben_nhan_giu = fields.Integer(u'Bên nhận giữ',default=1,copy=False)
    totrinh_id = fields.Many2one('dai_tgg.totrinh', string=u'Tờ trình',copy=False)
    title_ben_thu_3 = fields.Many2one('tonkho.title_cac_ben',string=u'Tiêu đề bên thứ 3',copy=False)
    ben_thu_3_ids = fields.Many2many('res.partner','ben_thu_3_stock_picking_relate','picking_id','partner_id',string=u'Bên thứ 3',copy=False)
    title_ben_thu_4 = fields.Many2one('tonkho.title_cac_ben',string=u'Tiêu đề bên thứ 4',copy=False)
    ben_thu_4_ids = fields.Many2many('res.partner','ben_thu_4_stock_picking_relate','picking_id','partner_id',string=u'Bên thứ 4',copy=False)
    texttemplate_id = fields.Many2one('tonkho.texttemplate',string=u"Mẫu lý do",domain=[('field_context','=','tonkho.stock.picking.field.ly_do')],copy=False)
    
    show_validate_ben_giao = fields.Boolean(compute='show_validate_ben_giao_')
#     is_diff_department = fields.Boolean(compute='is_diff_department_')
    is_same_department = fields.Boolean(compute='is_same_department_')
    is_validate_mode = fields.Boolean(compute='is_validate_mode_')
    ten_truoc_huy = fields.Char(readonly=True)
    
    lot_id = fields.Many2one('stock.production.lot')
#     start_date = fields.Date()
#     duration = fields.Float(digits=(6, 2), help="Duration in days")
#     end_date = fields.Date(string="End Date", store=True,
#         compute='_get_end_date', inverse='_set_end_date')
#     
#     @api.depends('start_date', 'duration')
#     def _get_end_date(self):
#         for r in self:
#             if not (r.start_date and r.duration):
#                 r.end_date = r.start_date
#                 continue
# 
#             # Add duration to start_date, but: Monday + 5 days = Saturday, so
#             # subtract one second to get on Friday instead
#             start = fields.Datetime.from_string(r.start_date)
#             duration = timedelta(days=r.duration, seconds=-1)
#             r.end_date = start + duration
# 
#     def _set_end_date(self):
#         for r in self:
#             if not (r.start_date and r.end_date):
#                 continue
# 
#             # Compute the difference between dates, but: Friday - Monday = 4 days,
#             # so add one day to get 5 days instead
#             start_date = fields.Datetime.from_string(r.start_date)
#             end_date = fields.Datetime.from_string(r.end_date)
#             r.duration = (end_date - start_date).days + 10
    @api.multi
    def is_validate_mode_(self):
        for r in self:
            r.is_validate_mode = self.env['ir.config_parameter'].sudo().get_param('tonkho.is_validate_mode')
        
    @api.depends('location_id','location_dest_id')
#     @api.multi
    def is_same_department_(self):
        for r in self:
            is_same_department = r.location_id.department_id == r.location_dest_id.department_id
            if not is_same_department:
                is_same_department = not r.location_id.department_id and r.location_id.cho_phep_khac_tram_chon
                is_same_department =  is_same_department or  (not r.location_dest_id.department_id and r.location_dest_id.cho_phep_khac_tram_chon)
            r.is_same_department = is_same_department
            
            
            
#     @api.multi
#     def is_diff_department_(self):
#         for r in self:
#             is_diff_department = r.location_id.department_id != r.location_dest_id.department_id
#             r.is_diff_department = is_diff_department
    
    @api.depends('location_id','location_dest_id')
    def show_validate_ben_giao_(self):
        for r in self:
            if r.is_validate_mode:
                ban_la_ben_giao = self.env.user.department_id == r.location_id.department_id 
                if ban_la_ben_giao and not r.is_same_department and r.state not in ('done','done_ben_giao') :
                    r.show_validate_ben_giao = True
                else:
                    r.show_validate_ben_giao = False
            else:
                r.show_validate_ben_giao = False


    @api.multi
    @api.depends('state', 'is_locked','location_id','location_dest_id')
    def _compute_show_validate(self):
        for picking in self:
            if picking.is_validate_mode:
                show_validate = False
                if picking.is_same_department :
                    if (self.env.user.department_id ==picking.location_id.department_id or self.env.user.department_id ==picking.location_dest_id.department_id) :
                        if self._context.get('planned_picking') and picking.state == 'draft':
                            show_validate = False
                        elif picking.state not in ('draft', 'confirmed', 'assigned') or not picking.is_locked:
                            show_validate = False
                        else:
                            show_validate = True
                else:
                    is_ban_la_ben_nhan = self.env.user.department_id == picking.location_dest_id.department_id
                    show_validate = False
                    if is_ban_la_ben_nhan:
                        if picking.state =='done_ben_giao':
                            show_validate = True
                        else:
                            show_validate = False
            else:
                if self._context.get('planned_picking') and picking.state == 'draft':
                    show_validate = False
                elif picking.state not in ('draft', 'confirmed', 'assigned') or not picking.is_locked:
                    show_validate = False
                else:
                    show_validate = True
#             show_validate = True ################warning nhớ xóa đi sau khi test report
            picking.show_validate = show_validate

                
                
    @api.multi
    def validate_cua_ben_giao(self):
        self.state = 'done_ben_giao'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done_ben_giao', u'Xác nhận bên giao'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")
        
    origin_pick_id = fields.Many2one('stock.picking')
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document", compute='origin_',store=True)
#     @api.multi
#     @api.depends('state', 'is_locked')
#     def _compute_show_validate(self):
#         for picking in self:
#             if self._context.get('planned_picking') and picking.state == 'draft':
#                 picking.show_validate = False
#             elif picking.state not in ('draft', 'confirmed', 'assigned') or not picking.is_locked:
#                 picking.show_validate = False
#             else:
#                 picking.show_validate = True
                
                
    @api.depends('origin_pick_id.name','origin_pick_id.ten_truoc_huy')
    def origin_(self):
        for r in self:
            if r.origin_pick_id:
                #
                if r.origin_pick_id.ten_truoc_huy:
                    first = u'Trả do hủy của '
                else:
                    first = u'Trả của '
                origin = first + r.origin_pick_id.name
                r.origin = origin
        
    
#     @api.multi
#     def copy(self, default=None):
# #         self.ensure_one()
# #         print ('**self.env.context',self.env.context)
# #         raise ValueError('on copy')
#         if default is None:
#             default = {}
# #         if 'name' not in default:
# #             default['name'] = _("%s (copy)") % self.name
#         if 'change_default_picking_copy' in self.env.context:
#             default['ban_giao_or_nghiem_thu'] = u'TRA'
#             
#         return super(StockPicking, self).copy(default=default)
    
    @api.onchange('ban_giao_or_nghiem_thu')
    @api.depends('ban_giao_or_nghiem_thu')
    def ma_bien_ban_(self):
        self.ma_bien_ban = self.ban_giao_or_nghiem_thu


#     def action_cancel_show_(self):
#         for r in self:
#             r.cancel_mode=self.env['ir.config_parameter'].sudo().get_param('tonkho.cancel_mode')
#     @api.onchange('department_id','ban_giao_or_nghiem_thu')
    @api.depends('department_id','ban_giao_or_nghiem_thu')
    def stt_trong_bien_ban_in_(self):
        domain = [('department_id','=',self.department_id.id),
                                                    ('ban_giao_or_nghiem_thu','=',self.ban_giao_or_nghiem_thu),
                                                    ('stt_trong_bien_ban_in','!=', 0),
                                                    ]
        if isinstance(self.id, int):
            domain.append(('id','!=',self.id))
        picking = self.env['stock.picking'].search(domain,limit=1,order='stt_trong_bien_ban_in desc')
        print ('**picking',picking,'picking.stt_trong_bien_ban_in',picking.stt_trong_bien_ban_in)
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
            picking.show_mark_as_todo = True
#             if picking.state == 'done' or picking.state == 'confirmed'  :
#                 picking.show_mark_as_todo = False
#             else:
#                 picking.show_mark_as_todo = True
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
#     @api.onchange('department_id','ban_giao_or_nghiem_thu','stt_trong_bien_ban_in')
    @api.depends('department_id','ban_giao_or_nghiem_thu','stt_trong_bien_ban_in')
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
    
#     @api.multi
#     def action_confirm(self):
#         # call `_action_confirm` on every draft move
#         
#         self.mapped('move_lines')\
#             .filtered(lambda move: move.state == 'draft')\
#             ._action_confirm()
#         # call `_action_assign` on every confirmed move which location_id bypasses the reservation
#         
#         print ("self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
#             .mapped('move_lines')",self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
#             ,self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
#             .mapped('move_lines'))
#         raise ValueError('dflsjkdfl kakak')
#         self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
#             .mapped('move_lines')._action_assign()
#         if self.env.context.get('planned_picking') and len(self) == 1:
#             action = self.env.ref('stock.action_picking_form')
#             result = action.read()[0]
#             result['res_id'] = self.id
#             result['context'] = {
#                 'search_default_picking_type_id': [self.picking_type_id.id],
#                 'default_picking_type_id': self.picking_type_id.id,
#                 'contact_display': 'partner_address',
#                 'planned_picking': False,
#             }
#             return result
#         else:
#             return True
        
        
    
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
#         todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            print ('**pick.move_line_ids',pick.move_line_ids)
             
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id) 
                print ('moves',moves,'ops',ops)
#                 raise ValueError('kakaka')
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
#                     todo_moves |= new_move

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
    def xem_print_theo_move_line(self):
        return {
             'type' : 'ir.actions.act_url',
             'url':'/report/html/tonkho.bao_cao_dieu_chuyen_theo_move_line/%s'%self.id,
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
    
    