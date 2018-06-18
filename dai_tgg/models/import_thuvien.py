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
    department_id = fields.Many2one('hr.department')
    update_number=fields.Integer()
    create_number=fields.Integer()
    skipupdate_number=fields.Integer()
    thong_bao_khac = fields.Char()
    trigger_model = fields.Selection([(u'kiemke',u'kiemke'),
                                    (u'vattu',u'vattu'),(u'kknoc',u'kknoc'),
                                    (u'cvi',u'cvi')
                                    ])
    dong_test = fields.Integer(default=0)#0 la initify vô hạn
    log = fields.Text()
    skip_field_cause_first_import = fields.Boolean(default=True)

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
    def get_tram_from_sheet_name(self):
        M = {'LTK':['LTK'],'PTR':['PTR'],'TTI':['TTI'],'BDG':['BDG','VTU']}
        count = 0
        map_count = 0
        for r in self.env['kknoc'].search([]):
            count +=1
            r.tram =convert_sheetname_to_tram(r.sheet_name)
            if r.tram:
                map_count +=1
        self.thong_bao_khac = 'so tram ltk, ptr %s'%map_count
    def map_kiemke_voi_noc(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kiemke'].search([]):
            ##print count
            if r.sn:
                mapping = self.env['kknoc'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    r.map_kknoc_id = mapping.id
            else:
                r.map_kknoc_id = False
            count +=1
        self.thong_bao_khac = u'Có %s kk mapping kknoc' %( so_luong_mapping)
        return True       
    def map_noc_voi_ltk(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kknoc'].search([]):
            ##print count
            if r.sn:
                mapping = self.env['vattu'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    ##print 'co %s mapping'%(so_luong_mapping)
                    r.map_ltk_id = mapping.id
            else:
                r.map_ltk_id = False
            count +=1
        self.thong_bao_khac = u'Có %s noc mapping ltk' %( so_luong_mapping)
        return True   
    def map_noc_voi_kiemke(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kknoc'].search([]):
            ##print count
            if r.sn:
                mapping = self.env['kiemke'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    ##print 'co %s mapping noc với kiểm kê'%(so_luong_mapping)
                    r.map_kiemke_id = mapping
            else:
                r.map_kiemke_id = False
            count +=1
        self.thong_bao_khac = u'Có %s noc mapping Kiểm kê' %( so_luong_mapping)
        return True   