from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ParkingZone(models.Model):
    _name = 'wc.parking.zone'
    _description = 'Zone de Parking'
    _order = 'name'

    name = fields.Char(string='Zone de parking', required=True)
    stadium_id = fields.Many2one('wc.stadium', string='Stade associé', required=True, ondelete='cascade')
    zone_type = fields.Selection([
        ('vip', 'VIP & Protocole'),
        ('public', 'Public'),
        ('media', 'Médias'),
        ('work', 'Staff & Volontaires'),
    ], string='Catégorie', required=True, default='public')
    total_capacity = fields.Integer(string='Capacité totale (places)', required=True, default=500)
    available_capacity = fields.Integer(string='Places libres', default=500)
    occupancy_rate = fields.Float(string="Taux d'occupation (%)", compute='_compute_occupancy_rate', store=True)

    @api.depends('total_capacity', 'available_capacity')
    def _compute_occupancy_rate(self):
        for record in self:
            if record.total_capacity > 0:
                record.occupancy_rate = ((record.total_capacity - record.available_capacity) / record.total_capacity) * 100
            else:
                record.occupancy_rate = 0.0

    @api.constrains('available_capacity', 'total_capacity')
    def _check_capacities(self):
        for record in self:
            if record.total_capacity < 0:
                raise ValidationError("La capacité totale ne peut pas être négative.")
            if record.available_capacity < 0:
                raise ValidationError("Les places libres ne peuvent pas être négatives.")
            if record.available_capacity > record.total_capacity:
                raise ValidationError("Les places libres ne peuvent pas dépasser la capacité totale.")
