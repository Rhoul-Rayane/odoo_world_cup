from odoo import models, fields, api


class Match(models.Model):
    _name = 'wc.match'
    _description = 'Match - Coupe du Monde 2030'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_time'

    name = fields.Char(string='Match', compute='_compute_name', store=True)
    team_a = fields.Char(string='Équipe A', required=True, tracking=True)
    team_b = fields.Char(string='Équipe B', required=True, tracking=True)
    stadium_id = fields.Many2one('wc.stadium', string='Stade', required=True, tracking=True)
    date_time = fields.Datetime(string='Date et heure', required=True, tracking=True)
    phase = fields.Selection([
        ('group', 'Phase de groupes'),
        ('round16', 'Huitièmes de finale'),
        ('quarter', 'Quarts de finale'),
        ('semi', 'Demi-finales'),
        ('third', 'Match pour la 3ème place'),
        ('final', 'Finale'),
    ], string='Phase', required=True, tracking=True)
    group = fields.Selection([
        ('A', 'Groupe A'), ('B', 'Groupe B'), ('C', 'Groupe C'), ('D', 'Groupe D'),
        ('E', 'Groupe E'), ('F', 'Groupe F'), ('G', 'Groupe G'), ('H', 'Groupe H'),
    ], string='Groupe')
    state = fields.Selection([
        ('planned', 'Planifié'),
        ('ongoing', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='planned', tracking=True)
    score_a = fields.Integer(string='Score Équipe A', default=0)
    score_b = fields.Integer(string='Score Équipe B', default=0)
    referee = fields.Char(string='Arbitre principal')
    attendance = fields.Integer(string='Affluence')
    notes = fields.Html(string='Notes')
    active = fields.Boolean(default=True)

    @api.depends('team_a', 'team_b')
    def _compute_name(self):
        for record in self:
            if record.team_a and record.team_b:
                record.name = f"{record.team_a} vs {record.team_b}"
            else:
                record.name = "Nouveau match"

    def action_start(self):
        self.write({'state': 'ongoing'})

    def action_end(self):
        self.write({'state': 'done'})
