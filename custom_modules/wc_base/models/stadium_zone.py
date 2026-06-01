from odoo import models, fields, api


class StadiumZone(models.Model):
    _name = 'wc.stadium.zone'
    _description = 'Zone de Stade'
    _order = 'stadium_id, name'

    name = fields.Char(string='Nom de la zone', required=True)
    stadium_id = fields.Many2one('wc.stadium', string='Stade', required=True, ondelete='cascade')
    zone_type = fields.Selection([
        ('tribune', 'Tribune'),
        ('vip', 'VIP'),
        ('press', 'Presse'),
        ('field', 'Terrain'),
        ('backstage', 'Backstage'),
        ('medical', 'Médical'),
        ('logistics', 'Logistique'),
    ], string='Type de zone', required=True)
    capacity = fields.Integer(string='Capacité')
    active = fields.Boolean(default=True)

    @api.depends('name', 'stadium_id')
    def _compute_display_name(self):
        for record in self:
            if record.stadium_id:
                record.display_name = f"{record.stadium_id.name} - {record.name}"
            else:
                record.display_name = record.name or ''
