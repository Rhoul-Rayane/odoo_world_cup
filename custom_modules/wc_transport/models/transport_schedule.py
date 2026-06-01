from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TransportSchedule(models.Model):
    _name = 'wc.transport.schedule'
    _description = 'Calendrier de Transport Match'
    _order = 'start_time'
    _rec_name = 'name'

    name = fields.Char(string='Nom', compute='_compute_name', store=True)
    match_id = fields.Many2one('wc.match', string='Match concerné', required=True, ondelete='cascade')
    line_id = fields.Many2one('wc.transport.line', string='Ligne de transport', required=True, ondelete='cascade')

    @api.depends('match_id', 'line_id')
    def _compute_name(self):
        for rec in self:
            match_name = rec.match_id.name or 'N/A'
            line_name = rec.line_id.name or 'N/A'
            rec.name = f"{line_name} — {match_name}"

    start_time = fields.Datetime(string='Début du service renforcé', required=True)
    end_time = fields.Datetime(string='Fin du service renforcé', required=True)
    frequency_minutes = fields.Integer(string='Fréquence (minutes)', default=5)
    planned_passengers = fields.Integer(string='Passagers prévus', default=5000)
    actual_passengers = fields.Integer(string='Passagers réels', default=0)

    @api.constrains('start_time', 'end_time')
    def _check_dates(self):
        for record in self:
            if record.start_time and record.end_time and record.end_time < record.start_time:
                raise ValidationError("L'heure de fin ne peut pas être antérieure à l'heure de début.")
