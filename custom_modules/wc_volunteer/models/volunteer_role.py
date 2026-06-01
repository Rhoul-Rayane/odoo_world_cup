from odoo import models, fields, api

class VolunteerRole(models.Model):
    _name = 'wc.volunteer.role'
    _description = 'Rôle Fonctionnel Volontaire'
    _order = 'name'

    name = fields.Char(string='Nom du rôle', required=True)
    functional_area = fields.Selection([
        ('accreditation', 'Accréditation'),
        ('media', 'Média & Presse'),
        ('ticketing', 'Billetterie'),
        ('transport', 'Transport & Logistique'),
        ('medical', 'Services Médicaux'),
        ('security', 'Sécurité & Gestion de Foule'),
        ('protocol', 'Protocole & VIP'),
    ], string='Secteur fonctionnel', required=True)
    description = fields.Text(string='Description des tâches')


class StadiumVolunteerQuota(models.Model):
    _name = 'wc.stadium.volunteer.quota'
    _description = 'Quota de Volontaires par Stade'
    _order = 'stadium_id, role_id'

    stadium_id = fields.Many2one('wc.stadium', string='Stade', required=True, ondelete='cascade')
    role_id = fields.Many2one('wc.volunteer.role', string='Rôle requis', required=True, ondelete='cascade')
    quota_required = fields.Integer(string='Quota requis (personnes)', required=True, default=10)
    quota_assigned = fields.Integer(string='Volontaires affectés', compute='_compute_quota_assigned')

    def _compute_quota_assigned(self):
        for record in self:
            record.quota_assigned = self.env['wc.volunteer'].search_count([
                ('assigned_stadium_id', '=', record.stadium_id.id),
                ('role_id', '=', record.role_id.id),
                ('state', '=', 'active')
            ])
