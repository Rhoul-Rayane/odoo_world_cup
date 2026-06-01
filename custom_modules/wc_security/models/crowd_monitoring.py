from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CrowdMonitoring(models.Model):
    _name = 'wc.crowd.monitoring'
    _description = 'Suivi de Densité de Foule'
    _order = 'last_updated desc'
    _rec_name = 'name'

    name = fields.Char(string='Nom', compute='_compute_name', store=True)

    match_id = fields.Many2one('wc.match', string='Match', required=True, ondelete='cascade')
    match_stadium_id = fields.Many2one('wc.stadium', related='match_id.stadium_id', readonly=True)
    
    stadium_zone_id = fields.Many2one(
        'wc.stadium.zone', 
        string='Zone du stade', 
        required=True, 
        domain="[('stadium_id', '=', match_stadium_id)]"
    )
    
    current_headcount = fields.Integer(string='Affluence instantanée (pers)', required=True, default=0)
    zone_area = fields.Float(string='Superficie de la zone (m²)', required=True, default=1000.0)
    density_per_sqm = fields.Float(string='Densité (pers/m²)', compute='_compute_density', store=True)
    
    safety_status = fields.Selection([
        ('green', 'Normal (Vert)'),
        ('orange', 'Attention (Orange)'),
        ('red', 'Critique (Rouge)'),
    ], string='Statut de sécurité', compute='_compute_safety_status', store=True)
    
    last_updated = fields.Datetime(string='Dernière mise à jour', default=fields.Datetime.now)

    @api.depends('match_id', 'stadium_zone_id')
    def _compute_name(self):
        for rec in self:
            match_name = rec.match_id.name or ''
            zone_name = rec.stadium_zone_id.name or ''
            rec.name = f"Foule — {match_name} ({zone_name})"

    @api.depends('current_headcount', 'zone_area')
    def _compute_density(self):
        for record in self:
            if record.zone_area > 0:
                record.density_per_sqm = record.current_headcount / record.zone_area
            else:
                record.density_per_sqm = 0.0

    @api.depends('density_per_sqm')
    def _compute_safety_status(self):
        for record in self:
            if record.density_per_sqm >= 4.0:
                record.safety_status = 'red'
            elif record.density_per_sqm >= 2.0:
                record.safety_status = 'orange'
            else:
                record.safety_status = 'green'

    @api.constrains('current_headcount', 'zone_area')
    def _check_crowd_values(self):
        for record in self:
            if record.current_headcount < 0:
                raise ValidationError("L'affluence de foule ne peut pas être négative.")
            if record.zone_area <= 0:
                raise ValidationError("La superficie de la zone doit être strictement supérieure à zéro.")
