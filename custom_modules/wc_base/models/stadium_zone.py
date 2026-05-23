from odoo import models, fields


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

    # Nom complet affiché
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.stadium_id.name} - {record.name}"
            result.append((record.id, name))
        return result
