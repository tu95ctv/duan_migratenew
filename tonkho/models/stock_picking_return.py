# -*- coding: utf-8 -*-
# Part of Odoo. See ICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"
    _rec_name = 'product_id'
    ml_id = fields.Many2one('stock.move.line')
    
class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
#     def create_returns(self):
# #         print ('self.env.context',self.env.context)
# #         raise ValueError('akaka')
#         new_picking_id,picking_type_id = super(ReturnPicking, self).create_returns()
#         picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
#         picking.write({'ban_giao_or_nghiem_thu':u'HUY'})
#         return res
# #     
    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError("You may only return one picking at a time!")
        res = super(ReturnPicking, self).default_get(fields)
        move_dest_exists = False
        product_return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking:
            res.update({'picking_id': picking.id})
            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings"))
#             for move in picking.move_lines:
            for ml in picking.move_line_ids:
#                 if move.scrapped:
#                     continue
                if ml.move_line_dest_ids:
                    move_dest_exists = True
#                     quantity = ml.product_qty - sum(ml.move_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).\
#                                                       mapped('move_line_ids').mapped('product_qty'))
                    print ("ml.move_line_dest_ids.mapped('qty_done')",ml.move_line_dest_ids.mapped('qty_done'))
                    print ("ml.move_line_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('qty_done')",ml.move_line_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('qty_done'))
                    quantity = ml.qty_done - sum(ml.move_line_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('qty_done'))
#                 quantity = ml.qty_done
                else:
                    quantity = ml.qty_done
                quantity = float_round(quantity, precision_rounding=ml.product_uom_id.rounding)
                print ("***quantity 2",quantity)
#                 raise ValueError('akakak')
                if not quantity:
                    continue
                product_return_moves.append((0, 0, {'product_id': ml.product_id.id, 'quantity': quantity, 'ml_id': ml.id, 'uom_id': ml.product_id.uom_id.id}))
            if not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': product_return_moves})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest_exists})
#             if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
#                 res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
#             if 'original_location_id' in fields:
#                 res.update({'original_location_id': picking.location_id.id})
#             if 'location_id' in fields:
#                 location_id = picking.location_id.id
#                 if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
#                     location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
#                 res['location_id'] = location_id
        return res
    
#     def create_returns(self):
#         for wizard in self:
#             new_picking_id, pick_type_id = wizard._create_returns()
#         # Override the context to disable all the potential filters that could have been set previously
#         ctx = dict(self.env.context)
#         ctx.update({
#             'search_default_picking_type_id': pick_type_id,
#             'search_default_draft': False,
#             'search_default_assigned': False,
#             'search_default_confirmed': False,
#             'search_default_ready': False,
#             'search_default_late': False,
#             'search_default_available': False,
#         })
#         return {
#             'name': _('Returned Picking'),
#             'view_type': 'form',
#             'view_mode': 'form,tree,calendar',
#             'res_model': 'stock.picking',
#             'res_id': new_picking_id,
#             'type': 'ir.actions.act_window',
#             'context': ctx,
#         }
#         
#         
#    

#     def create_returns(self):
#         for wizard in self:
#             
#             new_picking_id, pick_type_id = wizard._create_returns()
#         # Override the context to disable all the potential filters that could have been set previously
#         ctx = dict(self.env.context)
#         ctx.update({
#             'search_default_picking_type_id': pick_type_id,
#             'search_default_draft': False,
#             'search_default_assigned': False,
#             'search_default_confirmed': False,
#             'search_default_ready': False,
#             'search_default_late': False,
#             'search_default_available': False,
#         })
#         return {
#             'name': _('Returned Picking'),
#             'view_type': 'form',
#             'view_mode': 'form,tree,calendar',
#             'res_model': 'stock.picking',
#             'res_id': new_picking_id,
#             'type': 'ir.actions.act_window',
#             'context': ctx,
#         }
        
         
    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        new_picking = self.picking_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
#             'origin': _("Return of %s") % self.picking_id.name,# moi bo
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id,
            'origin_pick_id':self.picking_id.id,
            #moi them
            'ban_giao_or_nghiem_thu':u'TRA'
            })
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
#             if not return_line.move_id:
            if not return_line.ml_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values_ml_from_return_line(return_line, new_picking)
                r = return_line.ml_id.copy(vals)
                vals = {}
 
                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.ml_id.move_line_dest_ids.mapped('returned_move_ids')
                move_dest_to_link = return_line.ml_id.move_line_orig_ids.mapped('returned_move_ids')
                vals['move_line_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.ml_id]
                vals['move_line_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
#         for ml in picking.move_line_ids:
#             vals = self._prepare_move_default_values_ml(ml,new_picking)
#             new_ml = ml.copy(vals)    
#             new_ml.state = 'draft'    
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        else:
            print ('self._context',self._context)
#             raise ValueError('kakakak')
            if self._context.get('huy_bien_ban'):
                if not picking.ten_truoc_huy:
                    picking.ten_truoc_huy = picking.name
                picking.ban_giao_or_nghiem_thu = u'HUY'
#         new_picking.action_confirm()
 
#         action_confirm(self):
#         self.ghom_stock_move_lines()
#         new_picking.action_assign()
        return new_picking.id, picking_type_id
    
    def _prepare_move_default_values_ml_from_return_line(self,return_line,new_picking):
        vals = {
#             'product_id': return_line.product_id.id,
#             'product_uom_id': return_line.product_id.uom_id.id,
#             'product_uom_qty': return_line.quantity,
#             'product_uom': return_line.product_id.uom_id.id,
            'qty_done':return_line.quantity,
            'move_id':False,
            'picking_id': new_picking.id,
            'state': 'draft',
            'location_id': return_line.ml_id.location_dest_id.id,
            'location_dest_id': return_line.ml_id.location_id.id,
#             'qty_done':ml.qty_done,
             
#             'picking_type_id': new_picking.picking_type_id.id,
#             'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line.ml_id.id,
#             'procure_method': 'make_to_stock',
        }
        return vals
    
    def _prepare_move_default_values_ml(self,ml,new_picking):
        vals = {
#             'product_id': return_line.product_id.id,
#             'product_uom_qty': return_line.quantity,
#             'product_uom': return_line.product_id.uom_id.id,
            'move_id':False,
            'picking_id': new_picking.id,
            'state': 'draft',
            'location_id': ml.location_dest_id.id,
            'location_dest_id': ml.location_id.id,
            'qty_done':ml.qty_done,
             
#             'picking_type_id': new_picking.picking_type_id.id,
#             'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
#             'origin_returned_move_id': return_line.move_id.id,
#             'procure_method': 'make_to_stock',
        }
        return vals
    
    
    