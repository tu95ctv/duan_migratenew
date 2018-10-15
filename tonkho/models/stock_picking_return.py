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
#     is_chuyen_tiep = fields.Boolean()
    loai_tra_hay_chuyen_tiep = fields.Selection([('tra_do_huy',u'Trả do hủy'),('tra_do_muon',u'Trả do mượn'),('chuyen_tiep',u'Chuyển tiếp')],string=u'Loại trả vật tư')
    
    @api.onchange('loai_tra_hay_chuyen_tiep')
    def loai_tra_hay_chuyen_tiep_(self):
        if  self.loai_tra_hay_chuyen_tiep =='chuyen_tiep': # return
            rt  ={'domain':{'location_id':"[]"}}
        else:
            rt  ={}
        return rt
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
            for ml in picking.move_line_ids:
                if ml.move_line_dest_ids:
                    move_dest_exists = True
                    print ("ml.move_line_dest_ids.mapped('qty_done')",ml.move_line_dest_ids.mapped('qty_done'))
                    print ("ml.move_line_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('qty_done')",ml.move_line_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('qty_done'))
                    quantity = ml.qty_done - sum(ml.move_line_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).mapped('qty_done'))
                else:
                    quantity = ml.qty_done
                quantity = float_round(quantity, precision_rounding=ml.product_uom_id.rounding)
                if not quantity:
                    continue
                product_return_moves.append((0, 0, {'product_id': ml.product_id.id, 'quantity': quantity, 'ml_id': ml.id, 'uom_id': ml.product_id.uom_id.id}))
            if not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': product_return_moves})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest_exists})
        return res
    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        
        loai_tra_hay_chuyen_tiep = self._context.get('default_loai_tra_hay_chuyen_tiep','tra_do_muon')
        if loai_tra_hay_chuyen_tiep == 'tra_do_huy':
            ban_giao_or_nghiem_thu = u'TRA_DO_HUY'
        else:
            
            if self.env['ir.config_parameter'].sudo().get_param('tonkho.is_bg_or_nt_tra_do_muon'):
                if loai_tra_hay_chuyen_tiep == 'chuyen_tiep':
                    ban_giao_or_nghiem_thu = u'CHUYEN_TIEP'
                else:
                    ban_giao_or_nghiem_thu = u'TRA_DO_MUON'
            else:
                ban_giao_or_nghiem_thu = u'BBBG'
        
        new_picking = self.picking_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id,
            #moi them
            'origin_pick_id':self.picking_id.id,
            'ban_giao_or_nghiem_thu':ban_giao_or_nghiem_thu,
            'loai_tra_hay_chuyen_tiep':loai_tra_hay_chuyen_tiep
            })
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.ml_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values_ml_from_return_line(return_line, new_picking,loai_tra_hay_chuyen_tiep )
                ml = return_line.ml_id.copy(vals)
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
                ml.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        else:
            if loai_tra_hay_chuyen_tiep == 'tra_do_huy':
                if not picking.ten_truoc_huy:
                    picking.ten_truoc_huy = picking.name
                    picking.ban_giao_or_nghiem_thu = 'HUY'
                    
        print ('ban_giao_or_nghiem_thu***',ban_giao_or_nghiem_thu)
        if ban_giao_or_nghiem_thu == u'TRA_DO_HUY':
            print ('**button_validate')
            new_picking.button_validate()
        return new_picking.id, picking_type_id
    
    
    def _prepare_move_default_values_ml_from_return_line(self,return_line,new_picking, loai_tra_hay_chuyen_tiep):
        if loai_tra_hay_chuyen_tiep =='chuyen_tiep':
            location_dest_id = new_picking.location_dest_id.id
        else:
            location_dest_id = return_line.ml_id.location_id.id
        
        vals = {
            'qty_done':return_line.quantity,
            'move_id':False,
            'picking_id': new_picking.id,
            'state': 'draft',
            'location_id': return_line.ml_id.location_dest_id.id,
            'location_dest_id': location_dest_id,
            'origin_returned_move_id': return_line.ml_id.id,
        }
        return vals

    
    
    