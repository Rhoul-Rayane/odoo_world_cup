from odoo import models, fields


class Incident(models.Model):
    _name = 'wc.logistics.incident'
    _description = 'Incident / Signalement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'severity desc, create_date desc'

    name = fields.Char(string='Titre', required=True)
    description = fields.Text(string='Description détaillée', required=True)

    stadium_id = fields.Many2one('wc.stadium', string='Stade', required=True)
    zone_id = fields.Many2one('wc.stadium.zone', string='Zone',
                              domain="[('stadium_id', '=', stadium_id)]")
    match_id = fields.Many2one('wc.match', string='Match en cours')
    reporter_id = fields.Many2one('res.users', string='Signalé par',
                                   default=lambda self: self.env.user)

    incident_type = fields.Selection([
        ('security', 'Sécurité'),
        ('medical', 'Médical'),
        ('technical', 'Technique'),
        ('logistics', 'Logistique'),
        ('crowd', 'Gestion de foule'),
        ('weather', 'Météo'),
        ('other', 'Autre'),
    ], string='Type', required=True)

    severity = fields.Selection([
        ('1', 'Faible'),
        ('2', 'Moyen'),
        ('3', 'Élevé'),
        ('4', 'Critique'),
    ], string='Sévérité', required=True, default='2')

    state = fields.Selection([
        ('reported', 'Signalé'),
        ('in_progress', 'En cours de traitement'),
        ('resolved', 'Résolu'),
        ('closed', 'Clôturé'),
    ], string='Statut', default='reported', tracking=True)

    resolution = fields.Text(string='Résolution')
    resolved_date = fields.Datetime(string='Date de résolution')

    def action_start_treatment(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        self.write({'state': 'resolved', 'resolved_date': fields.Datetime.now()})

    def action_close(self):
        self.write({'state': 'closed'})
