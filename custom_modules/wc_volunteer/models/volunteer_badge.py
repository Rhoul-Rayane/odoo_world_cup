from odoo import models, fields

class VolunteerBadge(models.Model):
    _name = 'wc.volunteer.badge'
    _description = 'Badge de Gamification'
    _order = 'name'

    name = fields.Char(string='Nom du badge', required=True)
    description = fields.Text(string="Critères d'obtention")
    points_reward = fields.Integer(string='Points offerts', default=100)
    icon = fields.Binary(string='Icône du badge')
