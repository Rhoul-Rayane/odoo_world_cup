from odoo import models, fields, api

class Stadium(models.Model):
    _inherit = 'wc.stadium'

    location_id = fields.Many2one('stock.location', string='Emplacement de stockage', ondelete='set null')

    @api.model_create_multi
    def create(self, vals_list):
        stadiums = super(Stadium, self).create(vals_list)
        for stadium in stadiums:
            if not stadium.location_id:
                # Automatically create an internal location for this stadium
                parent_loc = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
                parent_id = parent_loc.id if parent_loc else False
                
                location = self.env['stock.location'].create({
                    'name': stadium.name,
                    'location_id': parent_id,
                    'usage': 'internal',
                })
                stadium.location_id = location.id
        return stadiums

    def write(self, vals):
        res = super(Stadium, self).write(vals)
        if 'name' in vals:
            for stadium in self:
                if stadium.location_id:
                    stadium.location_id.write({'name': vals['name']})
        return res

    @api.model
    def _register_hook(self):
        # Auto-heal: Create locations for any existing stadiums that don't have one
        stadiums = self.search([('location_id', '=', False)])
        if stadiums:
            parent_loc = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
            parent_id = parent_loc.id if parent_loc else False
            for stadium in stadiums:
                location = self.env['stock.location'].create({
                    'name': stadium.name,
                    'location_id': parent_id,
                    'usage': 'internal',
                })
                stadium.write({'location_id': location.id})
        return super(Stadium, self)._register_hook()
