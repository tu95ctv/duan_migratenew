# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import  convert_utc_to_gmt_7,name_compute,convert_odoo_datetime_to_vn_datetime,convert_odoo_datetime_to_vn_str,name_compute_char_join_rieng,convert_vn_datetime_to_utc_datetime,Convert_date_orm_to_str
from odoo.exceptions import ValidationError,UserError
import datetime
import sys
VERSION_INFO   = sys.version_info[0]

def skip_depends_if_not_congviec_decorator(depend_func):
    def wrapper(*args,**kargs):
        self = args[0]
        for r in self:
            if r.loai_record ==u'Công Việc':
                depend_func(r)
    return wrapper

def skip_depends_if_not_congviec_decorator_valid_diemtc(depend_func):
    def wrapper(*args,**kargs):
        self = args[0]
        for r in self:
            if not r.id:
                pass
            elif r.loai_record !=u'Công Việc':
                r.valid_diemtc =True
            else:
                depend_func(r)
    return wrapper
def het_time(r,TIME_ALLOW_SECONDS):
    TIME_ALLOW = datetime.timedelta(seconds=TIME_ALLOW_SECONDS)
    create_date =  fields.Datetime.from_string(r.create_date)
    delta_time =  datetime.datetime.now() - create_date
    return  delta_time>TIME_ALLOW   
    
    
def get_value_of_one_setting(self,fname,tien_to = 'dai_tgg.'):
    if VERSION_INFO==2:
        return self.env['ir.values'].get_default('ltk.config.settings', tien_to+ fname)
    else:
        return self.env['ir.config_parameter'].sudo().get_param(tien_to + fname)

class CamSua(models.Model):
    _name = 'camsua'
    _auto = False
    cam_sua = fields.Boolean(compute='cam_sua_',string=u'cấm sửa')
    cam_sua_do_chot =  fields.Boolean(compute='cam_sua_do_time_')
    cam_sua_do_time =  fields.Boolean(compute='cam_sua_do_time_')
    cam_sua_do_diff_user =  fields.Boolean(compute='cam_sua_do_diff_user_')
    ly_do_cam_sua_do_time = fields.Char(compute='cam_sua_do_time_')
    ly_do_cam_sua_do_diff_user = fields.Char(compute='cam_sua_do_diff_user_')
    is_admin = fields.Boolean(compute='is_admin_')
    ALLOW_WRITE_FIELDS_TIME = ['gio_ket_thuc','comment_ids']
    ALLOW_WRITE_FIELDS_DIFF_USER = ['gio_ket_thuc','comment_ids','percent_diemtt']
    ALLOW_WRITE_FIELDS_CHOT=[]
    IS_CAM_SUA_DO_CHOT = False
    @api.multi
    def is_admin_(self):
        for r in self:
            if self.user_has_groups('base.group_erp_manager'):
                r.is_admin = True
    @api.multi
    def cam_sua_(self):
        for r in self:
            r.cam_sua = r.cam_sua_do_time or r.cam_sua_do_diff_user
    @api.multi
    def cam_sua_do_time_(self):
        for r in self:
            if not r.id:
                r.ly_do_cam_sua_do_time = u'Không cấm sửa do new'
                r.cam_sua_do_time = False
            
#             elif self.env['ir.values'].get_default('ltk.config.settings', 'is_cam_sua_truoc_ngay'):
            elif get_value_of_one_setting(self,'is_cam_sua_truoc_ngay'):
#                 cam_sua_truoc_ngay = self.env['ir.values'].get_default('ltk.config.settings', 'cam_sua_truoc_ngay')
                cam_sua_truoc_ngay = get_value_of_one_setting(self,'cam_sua_truoc_ngay')
                if fields.Date.from_string(r.ngay_bat_dau) < fields.Date.from_string(cam_sua_truoc_ngay):
                    r.cam_sua_do_time = True
                    r.ly_do_cam_sua_do_time = u'cấm sửa do trước ngày'
                    r.cam_sua_do_chot = True
#             elif not self.env['ir.values'].get_default('ltk.config.settings', 'is_cam_sua_do_time'):
            elif not get_value_of_one_setting(self,'is_cam_sua_do_time'):
                r.ly_do_cam_sua_do_time = u'Không cấm sửa do is_cam_sua_do_time = False'
            else:
#                 TIME_ALLOW_SECONDS = self.env['ir.values'].get_default('ltk.config.settings', 'allow_edit_time')
                TIME_ALLOW_SECONDS = get_value_of_one_setting(self,'allow_edit_time')
                cam_sua = het_time(r,TIME_ALLOW_SECONDS)
                r.cam_sua_do_time =  cam_sua
                if cam_sua:
                    r.ly_do_cam_sua_do_time = u'cấm sửa do hết thời gian' 
                else:
                    r.ly_do_cam_sua_do_time = u'Không cấm sửa do chưa hết thời gian' 
    @api.multi
    def cam_sua_do_diff_user_(self):
        for r in self:
            if not r.id:
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do new'
                cam_sua_do_diff_user =  False
            elif self.user_has_groups('base.group_erp_manager'):
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do user là admin'
                cam_sua_do_diff_user =  False
            else:
                cam_sua_do_diff_user = r.create_uid != self.env.user 
                if cam_sua_do_diff_user:
                    r.ly_do_cam_sua_do_diff_user = u'Cấm do khác user'
                else:
                    r.ly_do_cam_sua_do_diff_user = u'Không cấm do cùng User'
            r.cam_sua_do_diff_user =  cam_sua_do_diff_user
    @api.multi
    def write(self,vals):
        res = super(CamSua,self).write(vals)
        return res
    
    @api.multi
    def unlink(self):
        for r in self:
            if r.cam_sua:
                raise UserError(u'Không được Xóa tại bạn không phải là chủ topic')
            else:
                if r.state != 'mark_delete':
                    raise UserError(u'Muốn Xóa thì phải Đánh Dấu Xóa trước đã')
#             else:
#                 if r.state !='ready_delete' and not r.is_admin:
#                     raise UserError(u'Bạn phải chuyển trạng thái qua Ready Delete đã rồi mới được xóa')
        res = super(CamSua, self).unlink()
        return res 
class DuyetDiem(models.TransientModel):
    _name = "dai_tgg.duyetdiem"
    @api.multi
    def multi_approved(self):
        active_ids = self._context.get('active_ids')
        if active_ids:
            cac_linh_ids = self.env.user.cac_linh_ids
            for r in self.env['cvi'].browse(active_ids):
                if r.is_sep:#or r.is_admin or (cac_linh_ids and (r.create_uid == r.env.user or r.user_id == r.env.user)):
                    r.state = 'approved'
                else:
                    raise UserError (u'Bạn không phải là lãnh đạo của nhân viên tạo record này')
        else:
            raise UserError (u'Bạn chưa chọn dòng nào')
    @api.multi
    def multi_confirmed(self):
        active_ids = self._context.get('active_ids')
        if active_ids:
            cac_linh_ids = self.env.user.cac_linh_ids
            for r in self.env['cvi'].browse(active_ids):
                if r.is_sep:# or r.is_admin or (cac_linh_ids and (r.create_uid == r.env.user or r.user_id == r.env.user)):
                    r.state = 'confirmed'
                else:
                    raise UserError (u'Bạn không phải là lãnh đạo của nhân viên tạo record này')
        else:
            raise UserError (u'Bạn chưa chọn dòng nào')
                
                
    
class Cvi(models.Model):
    _name = 'cvi'
    _parent_name = 'gd_parent_id'
#         _inherit = ['mail.thread']
    _inherit = ['camsua','cvisuco','mail.thread', 'mail.activity.mixin']

    _auto = True
    _order = "id desc"
    ALLOW_WRITE_FIELDS_TIME = ['gio_ket_thuc','comment_ids','cd_children_ids','gd_children_ids','percent_diemtt']
    ALLOW_WRITE_FIELDS_CHOT = ['gio_ket_thuc','comment_ids','cd_children_ids','gd_children_ids',]
    ALLOW_WRITE_FIELDS_DIFF_USER = ['gio_ket_thuc','comment_ids','cd_children_ids','gd_children_ids','percent_diemtc']
    IS_CAM_SUA_DO_CHOT = True
    
    
#     @api.multi
#     def action_ready_delete(self):
#         for r in self:
#             if r.state == 'approved':
#                 if r.is_sep or r.is_admin:
#                     r.state = 'ready_delete'
#                 else:
#                     raise UserError(u'Bạn không có quyến set từ Approve thành Ready Delete')
#             else:
#                 r.state = 'ready_delete'
    
    @api.multi
    def action_mark_delete(self):
        for r in self:
            if r.state == 'confirmed':
                r.state = 'mark_delete'
                
                
    @api.multi
    def action_confirmed(self):
        for r in self:
            if r.state == 'approved':
                if r.is_sep:# or r.is_admin:
                    r.state = 'confirmed'
                else:
                    raise UserError(u'Bạn không có quyến set từ Approve thành Confirm')
            else:
                r.state = 'confirmed'
    
    @api.multi
    def action_approved(self):
        for r in self:
            if r.is_sep:#or r.is_admin:
                r.state = 'approved'
            else:
                raise UserError(u'Bạn không có quyền aprroved')
            
                

    @api.onchange('user_id','create_uid','trig_field')
    def department_id_(self):
        for r in self:
            if r.user_id:
                r.department_id = r.user_id.department_id

    state = fields.Selection([
#                               ('ready_delete',u'Cho phép xóa'),
                              ('mark_delete',u'Đánh Dấu Để Xóa'),
                              ('confirmed',u'Xác Nhận'), ('approved',u'Lãnh Đạo đã duyệt'),
                          ],default='confirmed',required=True,string=u'Trạng thái')
    ti_le_chia_diem = fields.Float(digits=(6,2),string=u'Tỉ lệ chia điểm')
    id_for_pivot = fields.Integer(compute='name_',store=True)
    tvcv_id_name = fields.Char(compute='tvcv_id_name_',string=u'Thư Viện Công Việc',store=True)
    code= fields.Char(compute='code_',string=u'Mã Công Việc',store=True)
    diem_tvi = fields.Float(digits=(6,2),string=u'Điểm Thư Viện',compute='diem_tvi_',store=True,readonly=True)# 
    don_vi = fields.Many2one('donvi',string=u'Đơn vị tính',compute='don_vi_',store=True)
    so_luong = fields.Float(string=u'Số Lượng',default = 1,required=True,digit=(6,2))
    so_lan = fields.Integer(string=u'Số Lần',default = 1,required=True)
    tree_view_ref = fields.Char(compute='tree_view_ref_',default='dai_tgg.tvcv_list')
    search_view_ref = fields.Char(compute='tree_view_ref_',default='dai_tgg.tvcv_search')
    cvi_lien_quan_ids = fields.Many2many('cvi','cvi_cvi_relate','cvi_id','cvi_lien_quan_id', string=u'Công Việc/Sự Cố/ Sự Vụ Liên quan')
    gd_parent_id = fields.Many2one('cvi',string=u'Công Việc Giai Đoạn Cha',ondelete='cascade')
    gd_children_ids = fields.One2many('cvi','gd_parent_id',string=u'Các CV Giai Đoạn Con')
    cd_parent_id = fields.Many2one('cvi',string=u'Công Việc Chia Điểm Cha',ondelete='cascade')# ondelete='restrict' #ondelete='cascade', ondelete='set null'
    cd_children_ids = fields.One2many('cvi','cd_parent_id',string=u'Các CV Chia Điểm Con')
    hd_parent_id = fields.Many2one('cvi',string=u'Công Việc Hưởng điểm Cha',ondelete='cascade')# ondelete='restrict' #ondelete='cascade', ondelete='set null'
    hd_children_ids = fields.One2many('cvi','hd_parent_id',string=u'Các CV Hưởng Điểm Con')
    diem_goc = fields.Float(digits=(6,2),string=u'Điểm Góc',compute='diem_goc_',store=True)# 
    diemtc = fields.Float(digits=(6,2),compute='diemtc_',string=u'Điểm Nhân Viên',store=True)
    diem_remain_gd = fields.Float(compute='diem_remain_gd_',string=u'Điểm còn lại của giai đoạn con',store=True)
    slncl = fields.Integer(compute='slncl_',store=True,string=u'Số lượng người chia điểm')
    percent_diemtc = fields.Integer(default=100,string=u'Điểm LĐ/Điểm Nhân Viên (%)')
    diemld = fields.Float(digits=(6,2),compute='diemld_',string=u'Điểm Lãnh Đạo Chấm',store=True)
    valid_diemtc = fields.Boolean(compute='valid_diemtc_', string=u'Valid Điểm Nhân Viên',store=True)#
    loai_cvi = fields.Selection([(u'Single',u'Công Việc Đơn'),
                                 (u'Chia Điểm Cha',u'Chia Điểm Cha'),(u'Chia Điểm Con',u'Chia Điểm Con'),
                                 (u'Chung Điểm Cha',u'Chung Điểm Cha'),(u'Chung Điểm Con',u'Chung Điểm Con'),
                                 (u'Giai Đoạn Cha',u'Giai Đoạn Cha'), (u'Giai Đoạn Con',u'Giai Đoạn Con'),
                                 (u'Giai Đoạn Con và Chia Điểm Cha',u'Giai Đoạn Con và Chia Điểm Cha'),
                                 (u'Giai Đoạn Con và Giai Đoạn Cha',u'Giai Đoạn Con và Giai Đoạn Cha')
                                        ],compute='valid_diemtc_',store=True,string=u'Loại công việc')
    valid_cd = fields.Boolean(compute='valid_cd_',store=True)    
    valid_gd = fields.Boolean(compute='valid_gd_',store=True)  
    valid_diemtc_conclusion = fields.Selection([(u'Chia điểm không đủ 100%',u'Chia điểm không đủ 100%'),
                                  (u'Thiếu giai đoạn con',u'Thiếu giai đoạn con'),
                                  (u'Thiếu giai đoạn',u'Thiếu giai đoạn'),
                                  (u'Thiếu giai đoạn và Chia điểm không đủ 100%',u'Thiếu giai đoạn và Chia điểm không đủ 100%'),
                                  (u'Kiểm tra điểm OK',u'Kiểm tra điểm OK'),         
                                                           ],compute='valid_diemtc_',store=True,string=u'Kết luận Valid')
    
    #MIDLE FIELD , Trung gian
    len_gd_child = fields.Integer(compute='len_gd_child_',store=True)
    sum_gd_con = fields.Float(digits=(6,2),compute='sum_gd_con_',store=True)
    sum_cd_con = fields.Float(digits=(6,2),compute='sum_cd_con_',store=True)
    #compute field
    is_sep = fields.Boolean(compute='is_sep_')
    is_has_tvcv_con = fields.Boolean(compute='is_has_tvcv_con_')
    thu_vien_da_chon_list = fields.Char(compute='thu_vien_da_chon_list_')   
    cd_user_id = fields.Char(compute='cd_user_id_')  
     
    @api.depends('tvcv_id')
    def diem_tvi_(self):
        for r in self:
            if r.tvcv_id:
                r.diem_tvi = r.tvcv_id.diem
    @api.depends('tvcv_id')
    def tvcv_id_name_(self):
        for r in self:
            r.tvcv_id_name = r.tvcv_id.name
    
    @api.depends('tvcv_id')
    def code_(self):
        for r in self:
            r.code = r.tvcv_id.code
    @api.multi
    def cam_sua_do_diff_user_(self):
        for r in self:
            if not r.id:
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do new'
                cam_sua =  False
            elif self.user_has_groups('base.group_erp_manager'):
                r.ly_do_cam_sua_do_diff_user = u'Ko Cấm do user là admin'
                cam_sua =  False
            else:

                if ( r.user_id == self.env.user) or (r.create_uid == self.env.user):
                    cam_sua = False
                else:
                    cam_sua = True
                if cam_sua:
                    r.ly_do_cam_sua_do_diff_user = u'Cấm do khác user'
                else:
                    r.ly_do_cam_sua_do_diff_user = u'Không cấm do cùng User'
            r.cam_sua_do_diff_user =  cam_sua
    @api.depends('name')
    def is_admin_(self):
        rs = super(Cvi,self).is_admin_()
        return rs
    
    @api.depends('cd_children_ids','hd_children_ids')
    @skip_depends_if_not_congviec_decorator
    def cd_user_id_(self):
        for r in self:
            cd_user_id = []
            if r.cd_children_ids:
                cd_user_id = r.cd_children_ids.mapped('user_id.id')
            elif r.hd_children_ids:
                cd_user_id = r.hd_children_ids.mapped('user_id.id')
            if cd_user_id:
                cd_user_id.append(r.user_id.id)
                r.cd_user_id = cd_user_id
            
    @api.depends('tvcv_id.don_vi')
    @skip_depends_if_not_congviec_decorator
    def don_vi_(self):
        for r in self:
            r.don_vi = r.tvcv_id.don_vi
    @api.onchange('gd_children_ids')
    @skip_depends_if_not_congviec_decorator
    def thu_vien_da_chon_list_(self):
        for r in self:
#             if r.gd_children_ids:
            r.thu_vien_da_chon_list = r.gd_children_ids.mapped('tvcv_id.id')
            
    
    @api.depends('tvcv_id')
    @skip_depends_if_not_congviec_decorator
    def is_has_tvcv_con_(self):
        for r in self:
            if r.tvcv_id:
                r.is_has_tvcv_con = r.tvcv_id.is_has_children
    @api.multi
    def cam_sua_(self):
        for r in self:
            cam_sua = r.cam_sua_do_time or (r.cam_sua_do_diff_user and not r.is_sep) or (r.state =='approved' and not r.is_sep)
            r.cam_sua = cam_sua and not r.is_admin

    @api.multi
    @skip_depends_if_not_congviec_decorator
    def is_sep_(self): 
        cac_linh_ids = self.env.user.cac_linh_ids
        for r in self:
            if self.env.uid in r.user_id.cac_sep_ids.mapped('id') or self.user_has_groups('dai_tgg.cham_diem_group') \
            or (cac_linh_ids and (r.create_uid == r.env.user or r.user_id == r.env.user)) \
            or  self.user_has_groups('base.group_erp_manager'):# +  r.user_id.cac_sep_ids.cac_sep_ids.mapped('id'):
                r.is_sep = True
            else:
                r.is_sep = False
    ################# DEPEND##########################
    
    
    
    @api.depends(
                'cd_children_ids',# dành cho CHIA ĐIỂM CHA
                'cd_parent_id.cd_children_ids', # Trigger cho slncl CHIA ĐIỂM CON
                'len_gd_child',#moi add
                )      # khi form thay đổi bất cứ field nào thì chắc chắn cd_children_ids thay đổi vì ta sẽ luôn thay nó trong hàm write()
    @skip_depends_if_not_congviec_decorator
    def slncl_(self):
        for r in self:
            if r.cd_children_ids:
                r.slncl = len(r.cd_children_ids) + 1
            elif r.cd_parent_id:#CHIA ĐIỂM CON
                r.slncl = len(r.cd_parent_id.cd_children_ids) + 1
                
#                 #print u'222CD_CON  Ở SLNCL  CON^  id:%s,r.slncl:%s  ,r.cd_parent_id.cd_children_ids:%s 222'%(r.id,r.slncl,r.cd_parent_id.cd_children_ids)
            elif r.gd_children_ids:
                r.slncl=0
            else:
                r.slncl = 1
                
    @api.depends('gd_children_ids')
    @skip_depends_if_not_congviec_decorator
    def len_gd_child_(self):
        for r in self:
            r.len_gd_child = len(r.gd_children_ids)
    @api.depends('tvcv_id.diem','so_luong','so_lan','len_gd_child')
    @skip_depends_if_not_congviec_decorator
    def diem_remain_gd_(self):
        for r in self:
            if r.len_gd_child:
#                 r.diem_remain_gd = self.diem_remain_gd_compute(r)
                all_but_not_con_lai_s = r.gd_children_ids.filtered(lambda r: r.tvcv_id.id != self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id)
                all_but_not_con_lai_diem = list(map(lambda r: r.so_luong *r.so_lan * r.tvcv_id.diem,all_but_not_con_lai_s))
                diem_remain_gd =r.tvcv_id.diem*r.so_luong *r.so_lan -  sum(all_but_not_con_lai_diem)
                sai_so = 0.005* r.so_luong *r.so_lan*len(all_but_not_con_lai_diem)
                if abs(diem_remain_gd) < sai_so:
                    diem_remain_gd = 0
                r.diem_remain_gd = diem_remain_gd
 
    @api.depends('so_luong','so_lan', 'tvcv_id.diem','gd_parent_id.diem_remain_gd','loai_record')
    @skip_depends_if_not_congviec_decorator
    def diem_goc_(self):
        for r in self:
            if r.gd_parent_id: #GD CON
                if  r.tvcv_id.id == self.env.ref('dai_tgg.loaisuvu_viec_con_lai').id:
                    diem_remain_gd = r.gd_parent_id.diem_remain_gd
                    r.diem_goc = diem_remain_gd
                else:
                    r.diem_goc = r.so_luong * r.so_lan * r.tvcv_id.diem
            elif r.cd_parent_id:#Điểm góc CHIA ĐIỂM CON
                #r.diem_goc = 0#r.cd_parent_id.tvcv_id.diem *r.cd_parent_id.so_luong /r.slncl                #r.diem_goc = r.cd_parent_id.diem_goc/r.cd_parent_id.slncl
                r.diem_goc = r.cd_parent_id.tvcv_id.diem * r.cd_parent_id.so_luong * r.cd_parent_id.so_lan
            else:
                r.diem_goc = r.so_luong * r.so_lan * r.tvcv_id.diem


    @api.depends( 'slncl', 'diem_goc','cd_parent_id.diem_goc','len_gd_child','loai_record','ti_le_chia_diem')
    @skip_depends_if_not_congviec_decorator
    def diemtc_(self):
        for r in self:
                if r.cd_parent_id:#cv chia diem con
                    r.diemtc = r.cd_parent_id.diem_goc*r.ti_le_chia_diem/100
#                     r.diemtc = r.cd_parent_id.diem_goc/r.cd_parent_id.slncl
                elif r.slncl > 1:#CD Cha
                    r.diemtc = r.diem_goc*r.ti_le_chia_diem/100
#                     r.diemtc = r.diem_goc/r.slncl
                elif r.len_gd_child:  #giai doan cha
                    r.diemtc =0
#                     r.user_id = False
                else: 
                    r.diemtc = r.diem_goc           

    
    
    @api.depends('ti_le_chia_diem','slncl','cd_children_ids.ti_le_chia_diem')
    @skip_depends_if_not_congviec_decorator
    def sum_cd_con_(self):
        for r in self:
            if r.slncl > 1:
                sum_phan_tram = r.ti_le_chia_diem + sum(r.cd_children_ids.mapped('ti_le_chia_diem'))
                r.sum_cd_con =sum_phan_tram
    def valid_cd_chung_cha_con(self,r):
        abs_cd = abs(r.sum_cd_con - 100 )
        if  abs_cd <= 0.01*r.slncl:
            valid_cd = True
        else:
            valid_cd = False
        return valid_cd
    
    @api.depends('sum_cd_con','cd_parent_id.sum_cd_con')
    @skip_depends_if_not_congviec_decorator
    def valid_cd_(self):
        for r in self:
            if r.cd_parent_id:
                r.valid_cd = self.valid_cd_chung_cha_con(r.cd_parent_id)
            elif r.slncl > 1:
                r.valid_cd = self.valid_cd_chung_cha_con(r)

    #test git    
                
    @api.depends('diem_goc','len_gd_child','gd_children_ids.diem_goc')
    @skip_depends_if_not_congviec_decorator
    def sum_gd_con_(self):
        for r in self:
            if r.len_gd_child :
                r.sum_gd_con = sum(r.gd_children_ids.mapped('diem_goc'))
    
    def valid_gd_chung_cha_con(self,r):
        sai_so = abs(r.sum_gd_con - r.diem_goc )
        sai_so_lon_nhat = 0.005*r.len_gd_child*r.so_luong*r.so_lan
        if  sai_so <= sai_so_lon_nhat:
            valid_gd = True
        else:
            valid_gd = False
        return valid_gd
    
    @api.depends('diem_goc',
                        'sum_gd_con',
                         'gd_parent_id.sum_gd_con'
                 )
    @skip_depends_if_not_congviec_decorator
    def valid_gd_(self):
        for r in self:
            if r.gd_parent_id:
                r.valid_gd = self.valid_gd_chung_cha_con(r.gd_parent_id)
            elif r.len_gd_child:
                r.valid_gd = self.valid_gd_chung_cha_con(r)

    @api.depends('valid_gd','valid_cd','hd_children_ids','loai_record')
    @skip_depends_if_not_congviec_decorator_valid_diemtc
    def valid_diemtc_(self):
        for r in self:
            if not r.id:
                pass
            else:
                if r.gd_parent_id and r.slncl> 1:
                    r.loai_cvi = u'Giai Đoạn Con và Chia Điểm Cha'
                    r.valid_diemtc = r.valid_gd &  r.valid_cd
                    if not r.valid_gd and not r.valid_cd:
                        r.valid_diemtc_conclusion = u'Thiếu giai đoạn và Chia điểm không đủ 100%'
                    elif not r.valid_gd:
                        r.valid_diemtc_conclusion =  u'Thiếu giai đoạn'
                    elif not r.valid_cd:
                        r.valid_diemtc_conclusion =  u'Chia điểm không đủ 100%'
                elif r.cd_parent_id:# CD CON
                    r.loai_cvi = u'Chia Điểm Con'
                    r.valid_diemtc = r.valid_cd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Chia điểm không đủ 100%'
                elif  r.slncl > 1: # CD CHA
                    r.loai_cvi =u'Chia Điểm Cha'
                    r.valid_diemtc = r.valid_cd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Chia điểm không đủ 100%'
                elif r.len_gd_child: # GD CHA
                    r.loai_cvi =u'Giai Đoạn Cha'
                    r.valid_diemtc = r.valid_gd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Thiếu giai đoạn con'
                elif r.gd_parent_id:# GD CON
                    r.loai_cvi =u'Giai Đoạn Con'
                    r.valid_diemtc = r.valid_gd
                    if not r.valid_diemtc:
                        r.valid_diemtc_conclusion =  u'Thiếu giai đoạn'
                elif r.hd_parent_id:
                    r.loai_cvi = u'Chung Điểm Con'
                    r.valid_diemtc = True
                elif r.hd_children_ids:
                    r.loai_cvi = u'Chung Điểm Cha'
                    r.valid_diemtc = True
                else: # SINGLE
                    r.loai_cvi = u'Single'
                    r.valid_diemtc = True
                if r.valid_diemtc ==True:
                    r.valid_diemtc_conclusion = u'Kiểm tra điểm OK'
    @api.depends('percent_diemtc',
                 'diemtc')
    @skip_depends_if_not_congviec_decorator
    def diemld_(self):
        for r in self:
            r.diemld = r.diemtc * r.percent_diemtc /100
    
    
          
                    
    ###################contrains##############

    
    def get_parent_value_for_child(self,r,update_field_list,cd_parent_id_or_gd_parent_id):
        update_dict = {}
        for field in update_field_list:
            parent_id = getattr(r,cd_parent_id_or_gd_parent_id)
            fields = r._fields
            if fields[field].type=='many2one':
                update_dict[field] = getattr(parent_id,field).id
            elif fields[field].type=='many2many' or fields[field].type=='one2many':
                update_dict[field] =[(6, False,  getattr(parent_id,field).ids)]
            else:
                update_dict[field] =getattr(parent_id,field)
        return update_dict
 
    def update_dict_for_child_when_update_parent(self,r,update_field_list):
        update_dict = {}
        write_create_parent_dict = self._context['write_create_parent_dict']
        fields = r._fields
        for field in update_field_list:
            if field in write_create_parent_dict:
                if fields[field].type=='many2one':
                    update_dict[field] = getattr(r,field).id
                elif fields[field].type=='many2many' or fields[field].type=='one2many':
                    update_dict[field] =[(6, False,  getattr(r,field).ids)]
                else:
                    update_dict[field] =getattr(r,field)
        return update_dict
 
    @api.constrains('so_luong','so_lan','department_ids')
    def gd_parent_constrains(self):
        for r in self:
            if r.gd_children_ids:
                update_field_list = ['so_luong','so_lan','department_ids']
                update_dict = self.update_dict_for_child_when_update_parent(r,update_field_list)
                for child in r.gd_children_ids:
                    child.write(update_dict)        
   
    @api.constrains('gd_parent_id') # khi sinh ra
    def gd_children_constrains(self):
        for r in self:
            if r.gd_parent_id:
                update_field_list = ['so_luong','so_lan', 'department_ids']
                update_dict = self.get_parent_value_for_child(r,update_field_list,'gd_parent_id')
                r.write(update_dict)
#                 
    ## CONSTRAINS của chia điểm
    @api.constrains('tvcv_id','so_luong','so_lan','gio_ket_thuc','gio_bat_dau','department_ids','noi_dung')
    def cd_parent_constrains(self):
        for r in self:
            if r.cd_children_ids:
                update_field_list = ['tvcv_id','so_luong','gio_ket_thuc','gio_bat_dau','so_lan','department_ids','noi_dung']
                update_dict_of_child = self.update_dict_for_child_when_update_parent(r,update_field_list)
                for cd_child in r.cd_children_ids:
                    cd_child.write(update_dict_of_child)
 
    @api.constrains('cd_parent_id')
    def cd_children_constrains(self):
        for r in self:
            if r.cd_parent_id:
                update_field_list = ['tvcv_id','so_luong','gio_ket_thuc','gio_bat_dau','so_lan', 'department_ids','noi_dung']
                update_dict = self.get_parent_value_for_child(r,update_field_list,'cd_parent_id')
                r.write(update_dict)
        
    ### chung điểm
    
    @api.constrains('tvcv_id','so_luong','so_lan','gio_ket_thuc','gio_bat_dau','department_ids','noi_dung')
    def chd_parent_constrains(self):
        for r in self:
            try:
                if r.hd_children_ids:
                    update_field_list = ['tvcv_id','so_luong','gio_ket_thuc','gio_bat_dau','so_lan','department_ids','noi_dung']
                    update_dict_of_child = self.update_dict_for_child_when_update_parent(r,update_field_list)
                    for cd_child in r.hd_children_ids:
                        cd_child.write(update_dict_of_child)
            except exceptions as e:
                raise ValueError(e)
 
    @api.constrains('hd_parent_id')
    def chd_children_constrains(self):
        try:
            for r in self:
                if r.hd_parent_id:
                    update_field_list = ['tvcv_id','so_luong','gio_ket_thuc','gio_bat_dau','so_lan', 'department_ids','noi_dung']
                    update_dict = self.get_parent_value_for_child(r,update_field_list,'hd_parent_id')
                    r.write(update_dict)
        except exceptions as e:
            raise ValueError(e)
    
    
                
    def constrains_cha_con(self,r):    # r là cha, check coi thư viện công việc của những thằng con có phải là con của thư viện cv của thằng cha
        viec_con_lai = self.env.ref('dai_tgg.loaisuvu_viec_con_lai')
        check_list = map(lambda i:i.tvcv_id.parent_id !=r.tvcv_id and i.tvcv_id !=viec_con_lai,r.gd_children_ids)
        if any(check_list):
            raise ValidationError(u'Có ít nhất 1 Giai Đoạn Con có thư viện công việc không phải là con của CV Giai Đoạn Cha')
        tvcv_ids = [i.tvcv_id.id for i in  r.gd_children_ids]
        if len(tvcv_ids) != len(set(tvcv_ids)):
            raise ValidationError(u'Giai Đoạn con có duplicate ')
     
#     @api.constrains('tvcv_id')
    @api.constrains('gd_children_ids')# khi con của thằng cha thay đổi
    def check_thu_vien_con_in_gd_childs(self):
        for r in self:
            if r.gd_children_ids:
                self.constrains_cha_con(r)
                r.user_id = False
            elif r.gd_parent_id:
                self.constrains_cha_con(r.gd_parent_id)
    @api.constrains('slncl')
    def slncl_constrains(self):
        for r in self:
#             print 'fields.Datetime.from_string(r.write_date)',fields.Datetime.from_string(r.write_date),'fields.Datetime.from_string(r.create_date)',fields.Datetime.from_string(r.create_date)
#             print "r._context.get('create')",r._context.get('create')
            if r.slncl > 1 and fields.Datetime.from_string(r.create_date)  == fields.Datetime.from_string(r.write_date):
                ti_le_chia_diem = 100.0/r.slncl
                r.ti_le_chia_diem = ti_le_chia_diem
                if r.cd_parent_id:
                    r.cd_parent_id.write({'ti_le_chia_diem':ti_le_chia_diem})
                    r.cd_parent_id.cd_children_ids.write({'ti_le_chia_diem':ti_le_chia_diem})
#                 print 'ti_le_chia_diem',ti_le_chia_diem,'r.ti_le_chia_diem',r.ti_le_chia_diem,'r.ti_le_chia_diem==ti_le_chia_diem',r.ti_le_chia_diem==ti_le_chia_diem,'r.ti_le_chia_diem==33.33',r.ti_le_chia_diem==33.33
                
    @api.constrains('loai_record','user_id')
    def user_id_constrains(self):
        for r in self:
            if r.loai_record == u'Công Việc':
                if not r.gd_children_ids:
                    if not r.user_id:
                        raise ValidationError (u'Bạn phải nhập "Nhân Viên Làm" ')
              
                if r.cd_parent_id:
                    user_ids = [i.user_id.id for i in  r.cd_parent_id.cd_children_ids]
                    user_ids.append(r.cd_parent_id.user_id.id)
                    if len(user_ids) != len(set(user_ids)):
                        raise ValidationError(u'Có chia điểm con Trùng') 
                elif r.hd_parent_id: 
                    user_ids = [i.user_id.id for i in  r.hd_parent_id.hd_children_ids]
                    user_ids.append(r.hd_parent_id.user_id.id)
                    if len(user_ids) != len(set(user_ids)):
                        raise ValidationError(u'Có Hưởng điểm con Trùng')                        
           
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        active_ctr_id = context.get('active_ctr_id',False)
        if active_ctr_id != False:
            new_args = ['|',('ctr_ids','=',active_ctr_id)]
            new_args.extend(args)
            args = new_args
        return super(Cvi, self).search(args, offset, limit, order, count=count)           
    
    @api.model
    def create(self, vals):
        new_ctx = dict(self._context, **{'write_create_parent_dict':vals})
        cv = super(Cvi, self.with_context(new_ctx)).create(vals)
        return cv

    @api.multi
    def write(self, vals):
        new_ctx = dict(self._context, **{'write_create_parent_dict':vals})
        res = super(Cvi, self.with_context(new_ctx)).write(vals)
        return res    
    
    
    

    
