# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
import re
from odoo.addons.dai_tgg.models.tao_instance_new import importthuvien
# from odoo.addons.dai_tgg.models.tao_instance import import_strect

M = {'LTK':['LTK'],'PTR':['pas'],'TTI':['TTI'],'BDG':['BDG'],'VTU':['VTU']}
def convert_sheetname_to_tram(sheet_name):
    if sheet_name ==False:
        return False
    else:
        for tram,key_tram_list in M.items():
            for key_tram in key_tram_list:
                rs = re.search(key_tram,sheet_name)
                if rs:
                    find_tram = tram
                    return find_tram
        return sheet_name  

class ImportThuVien(models.Model):
    _name = 'importthuvien' 
    type_choose = fields.Selection([
        (u'stock.inventory.line',u'stock.inventory.line'),
        (u'stock.inventory.line.tkt.vtdc',u'stock.inventory.line.tkt.vtdc'),
        (u'Product',u'Product'),
        (u'Thư viện công việc',u'Thư viện công việc'),
                                    (u'User',u'User')
                                    #,(u'Công Ty',u'Công Ty')
                                    ,(u'Department',u'Department')
                                    ,(u'Partner',u'Partner')
                                    ,(u'location partner',u'location partner')
                                    ,(u'Stock Location',u'Stock Location')
                                    ,(u'stock production lot',u'stock production lot')
                                    ,(u'Kiểm Kê',u'Kiểm Kê'),(u'Vật Tư LTK',u'Vật Tư LTK')
                                    ,(u'x',u'x'),(u'640',u'640G 1850 ')
                                    ,(u'INVENTORY_240G',u'INVENTORY_240G')
                                    ,(u'INVENTORY_RING_NAM_CIENA',u'INVENTORY_RING_NAM_CIENA')
                                    ,(u'Inventory-120G',u'Inventory-120G')
                                    ,(u'Inventory-330G',u'Inventory-330G')
                                    ,(u'INVENTORY-FW4570',u'INVENTORY-FW4570')
                                    ,(u'INVETORY 1670',u'INVETORY 1670')
                                    ,(u'iventory hw8800',u'iventory hw8800')
                                    ,(u'iventory7500',u'iventory7500')
                                    ],required = True)
    sheet_name = fields.Selection([(u'Vô tuyến',u'Vô tuyến'),(u'Chuyển Mạch (IMS, Di Động)',u'Chuyển Mạch (IMS, Di Động)'),
                                   (u'Truyền dẫn',u'Truyền dẫn'),(u'IP (VN2, VNP)',u'IP (VN2, VNP)'),
                                   (u'GTGT',u'GTGT'),(u'XFP, SFP các loại',u'XFP, SFP các loại')  ])
    file = fields.Binary()
    filename = fields.Char()
    name_inventory_suffix = fields.Char()
    department_id = fields.Many2one('hr.department')
    update_number=fields.Integer()
    create_number=fields.Integer()
    skipupdate_number=fields.Integer()
    thong_bao_khac = fields.Char()
    trigger_model = fields.Selection([(u'kiemke',u'kiemke'),
                                    (u'vattu',u'vattu'),
                                    (u'kknoc',u'kknoc'),
                                    (u'cvi',u'cvi'),
                                    (u'stock.production.lot',u'stock.production.lot')
                                    ])
    dong_test = fields.Integer(default=0)#0 la initify vô hạn
    log = fields.Text()
    skip_field_cause_first_import = fields.Boolean(default=True)
    begin_row = fields.Integer(default=0)
#     location_id = fields.Many2one('stock.location')
    running_or_prepare = fields.Selection([('running',u'Đang chạy'),('prepare',u'Dự phòng')])
    import_location_id = fields.Many2one('stock.location')
    imported_number_of_row = fields.Integer()
    inventory_id = fields.Many2one('stock.inventory')
    test_result_1 = fields.Text()
    test_result_2 = fields.Text()
    test_result_3 = fields.Text()
    line_not_has_quant =  fields.Text()
    @api.onchange('type_choose')
    def import_location_id_(self):
#         adict = {'stock.inventory.line':'prepare','stock.inventory.line.tkt.vtdc':'running'}
        if self.type_choose == u'stock.inventory.line':
            self.import_location_id = self.env['stock.location'].search([('name','=',u'LTK Dự Phòng')]).id
        elif self.type_choose == u'stock.inventory.line.tkt.vtdc':
            self.import_location_id = self.env['stock.location'].search([('name','=',u'LTK Đang Chạy')]).id
    def check_stt_inventory_line_old(self):
        rs = self.env['stock.inventory.line'].search([('inventory_id','=',self.inventory_id.id)], order='stt asc')
        rs2 = self.env['stock.inventory.line'].search([('inventory_id','=',self.inventory_id.id)], order='stt desc',limit=1)
        last_stt = rs2.stt
        kq = set(rs.mapped('stt'))
        self.test_result_1  = kq
        set_2 = set(range(1,last_stt))
        self.test_result_2= last_stt
        rs3 = set_2 - kq
        self.test_result_3 = sorted(rs3) 
    def check_line_khong_co_quant_va_khong_co_qty(self):
        rs1 = self.inventory_id.line_ids
        khong_co_so_luong =  sorted( rs1.filtered(lambda r: not  r.product_qty ).mapped('stt'))
        co_so_luong_but_khong_co_quant = sorted( rs1.filtered(lambda r: r.product_qty and not r.quant_ids).mapped('stt'))
        self.test_result_3 ='co_so_luong_but_khong_co_quant' + '\n%s'%co_so_luong_but_khong_co_quant
        self.test_result_2= 'khong_co_so_luong \n%s'%khong_co_so_luong
    def check_stt_inventory_line(self):
        rs1 = self.inventory_id.line_ids
        rs2 = rs1.mapped('quant_ids').filtered(lambda r: r.location_id.usage=='internal')
        rs3 = sorted(rs2.mapped('stt'))
#         rs2 =sorted( rs1.filtered(lambda r: r.product_qty and not r.quant_ids).mapped('stt'))
        self.test_result_1 =len(rs1)
        self.test_result_2 =len(rs2)
        self.test_result_3= rs3
    def test_code(self):
        self.env['stock.inventory'].browse([13]).line_ids.unlink()
    def trigger(self):
        if self.trigger_model:
            count = 0
            self.env[self.trigger_model].search([]).write({'trig_field':'ok'})

        else:
            raise UserWarning(u'Bạn phải chọn trigger model')
    def importthuvien(self):
        importthuvien(self)
        return True
    def import_strect(self):
        pass
#         import_strect(self)
        return True
#     def get_tram_from_sheet_name(self):
#         M = {'LTK':['LTK'],'PTR':['PTR'],'TTI':['TTI'],'BDG':['BDG','VTU']}
#         count = 0
#         map_count = 0
#         for r in self.env['kknoc'].search([]):
#             count +=1
#             r.tram =convert_sheetname_to_tram(r.sheet_name)
#             if r.tram:
#                 map_count +=1
#         self.thong_bao_khac = 'so tram ltk, ptr %s'%map_count
#     def map_kiemke_voi_noc(self):
#         so_luong_mapping = 0
#         count = 0
#         for r in self.env['kiemke'].search([]):
#             ##print count
#             if r.sn:
#                 mapping = self.env['kknoc'].search([('sn','=',r.sn)],limit=1)
#                 if mapping:
#                     so_luong_mapping +=1
#                     r.map_kknoc_id = mapping.id
#             else:
#                 r.map_kknoc_id = False
#             count +=1
#         self.thong_bao_khac = u'Có %s kk mapping kknoc' %( so_luong_mapping)
#         return True       
#     def map_noc_voi_ltk(self):
#         so_luong_mapping = 0
#         count = 0
#         for r in self.env['kknoc'].search([]):
#             ##print count
#             if r.sn:
#                 mapping = self.env['vattu'].search([('sn','=',r.sn)],limit=1)
#                 if mapping:
#                     so_luong_mapping +=1
#                     ##print 'co %s mapping'%(so_luong_mapping)
#                     r.map_ltk_id = mapping.id
#             else:
#                 r.map_ltk_id = False
#             count +=1
#         self.thong_bao_khac = u'Có %s noc mapping ltk' %( so_luong_mapping)
#         return True   
#     def map_noc_voi_kiemke(self):
#         so_luong_mapping = 0
#         count = 0
#         for r in self.env['kknoc'].search([]):
#             ##print count
#             if r.sn:
#                 mapping = self.env['kiemke'].search([('sn','=',r.sn)],limit=1)
#                 if mapping:
#                     so_luong_mapping +=1
#                     ##print 'co %s mapping noc với kiểm kê'%(so_luong_mapping)
#                     r.map_kiemke_id = mapping
#             else:
#                 r.map_kiemke_id = False
#             count +=1
#         self.thong_bao_khac = u'Có %s noc mapping Kiểm kê' %( so_luong_mapping)
#         return True   