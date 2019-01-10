# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.addons.dai_tgg.models.model_dict_folder.tao_instance_new import importthuvien
from lxml import etree

class Inventory(models.Model):
    _inherit = "stock.inventory"
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure',
        )
    negative_product_select =  fields.Boolean()
    file = fields.Binary(string=u'File để import')
    filename = fields.Char()
    log = fields.Text(string=u'Log import file')
    sheet_name = fields.Char(u'Tên sheet(Nếu bỏ trống lấy sheet đầu, all => tất cả các sheets)',help=u'Nếu bỏ trống lấy sheet đầu, all => tất cả các sheets')
#     allow_product_qty_dieu_chinh = fields.Boolean(default=True)

    
    
    
    
    @api.multi
    def import_file(self):
#         for inventory in self.filtered(lambda x: x.state not in ('done','cancel')):
            
            importthuvien(self,
                           key=u'stock.inventory.line.tong.hop.ltk.dp.tti.dp',
                           key_tram='key_ltk',mode=u'2')
            if self.state not in ('done','cancel'):
                vals = {'state': 'confirm', 'date': fields.Datetime.now()}
                self.write(vals)
        
        
        
    @api.onchange('negative_product_select')
    
    
    
    def negative_product_select_(self):
        return {'domain':{'line_ids':[('theoretical_qty','<',0)]}}
#         if self.negative_product_select:
#             return {'domain':{'line_ids':[('theoretical_qty','<',0)]}}
#         else:
#             return {'domain':{'line_ids':[]}}
            
    @api.onchange('filter')
    def onchange_filter(self):
        if self.filter == 'product':
            self.exhausted = True
        else:
            self.exhausted = False
            if self.filter not in ('product', 'product_owner'):
                self.product_id = False
            if self.filter != 'lot':
                self.lot_id = False
            if self.filter not in ('owner', 'product_owner'):
                self.partner_id = False
            if self.filter != 'pack':
                self.package_id = False
            if self.filter != 'category':
                self.category_id = False
            if self.filter == 'vat_tu_am':
                self.negative_product_select = True
       
            
            
#     @api.onchange('filter')
#     def onchange_filter2(self):
#         if self.filter == 'vat_tu_am':
#             self.negative_product_select = True
#         else:
#             self.negative_product_select = False
            
            
        
        
    def _get_inventory_lines_values(self):
        # TDE CLEANME: is sql really necessary ? I don't think so
        locations = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
        domain = ' location_id in %s'
        args = (tuple(locations.ids),)

        vals = []
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']
        # Empty recordset of products to filter
        products_to_filter = self.env['product.product']

        # case 0: Filter on company
        if self.company_id:
            domain += ' AND company_id = %s'
            args += (self.company_id.id,)
        
        #case 1: Filter on One owner only or One product for a specific owner
        if self.partner_id:
            domain += ' AND owner_id = %s'
            args += (self.partner_id.id,)
        #case 2: Filter on One Lot/Serial Number
        if self.lot_id:
            domain += ' AND lot_id = %s'
            args += (self.lot_id.id,)
        #case 3: Filter on One product
        if self.product_id:
            domain += ' AND product_id = %s'
            args += (self.product_id.id,)
            products_to_filter |= self.product_id
        #case 4: Filter on A Pack
        if self.package_id:
            domain += ' AND package_id = %s'
            args += (self.package_id.id,)
        #case 5: Filter on One product category + Exahausted Products
        if self.category_id:
            categ_products = Product.search([('categ_id', '=', self.category_id.id)])
            domain += ' AND product_id = ANY (%s)'
            args += (categ_products.ids,)
            products_to_filter |= categ_products
        
        
        if self.negative_product_select:
            domain += ' AND quantity < %s'
            args += (0,)

        self.env.cr.execute("""SELECT product_id, sum(quantity) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
            FROM stock_quant
            WHERE %s
            GROUP BY product_id, location_id, lot_id, package_id, partner_id """ % domain, args)

        for product_data in self.env.cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)
        if self.exhausted:
            exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
            vals.extend(exhausted_vals)
        return vals
    
    
    
    
    @api.model
    def _selection_filter(self):
#         """ Get the list of filter allowed according to the options checked
#         in 'Settings\Warehouse'. """
#         res_filter = [
#             ('none', _('All products')),
#             ('category', _('One product category')),
#             ('product', _('One product only')),
#             ('partial', _('Select products manually'))]
# 
#         if self.user_has_groups('stock.group_tracking_owner'):
#             res_filter += [('owner', _('One owner only')), ('product_owner', _('One product for a specific owner'))]
#         if self.user_has_groups('stock.group_production_lot'):
#             res_filter.append(('lot', _('One Lot/Serial Number')))
#         if self.user_has_groups('stock.group_tracking_lot'):
#             res_filter.append(('pack', _('A Pack')))
        res_filter = super(Inventory, self)._selection_filter()
        res_filter.append( ('vat_tu_am', _(u'vật tư có số lượng âm')))
        return res_filter
    
    
    @api.multi
    def product_uom_id_oc(self):
        for r in self.line_ids:
            r.product_id.uom_id = self.product_uom_id
            r.product_uom_id = self.product_uom_id
    
    #over write origin
    def action_done(self):
        return super(Inventory, self.with_context(action_done_from_stock_inventory=True)).action_done()
    
    
    @api.model
    def _default_location_id_d4_write(self):
        department_id = self.env.user.department_id
        if not department_id:
            raise UserError(_(u'You must define a department_id for you') )
        default_location_id = department_id.default_location_id
        if default_location_id:
            return default_location_id.id
        else:
            raise UserError(_('You must define a default_location_id of department_id.') )
    @api.model
    def default_get(self, fields):
        res = super(Inventory, self).default_get(fields)
        res['location_id'] = self._default_location_id_d4_write()
        return res

    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Inventory, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type =='form':
            doc = etree.XML(res['arch'])
            nodes =  doc.xpath("//field[@name='location_id']")
            if len(nodes):
                domain = "[('is_kho_cha','=',True)]"
                node = nodes[0]
                node.set('domain',domain )
                res['arch'] = etree.tostring(doc, encoding='unicode')
#             res['fields']['location_id']['domain'] = [('is_kho_cha','=',True)]
#             res['fields']['location_id']['string'] = u'Kho để kiểm'
        return res
    