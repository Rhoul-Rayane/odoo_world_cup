from odoo import models, fields, api

class Tournament(models.Model):
    _name = 'wc.tournament'
    _description = 'Coupe du Monde - Édition Historique'
    _order = 'year desc'

    key = fields.Char(string='Clé Tournoi', required=True, index=True)
    name = fields.Char(string="Nom de l'édition", required=True)
    year = fields.Integer(string='Année', required=True)
    host_country = fields.Char(string='Pays Hôte')
    winner = fields.Char(string='Vainqueur')
    teams_count = fields.Integer(string="Nombre d'équipes")
    matches_count = fields.Integer(string='Nombre de matchs')
    goals_count = fields.Integer(string='Nombre de buts')

    _key_uniq = models.Constraint(
        'unique(key)',
        'La clé du tournoi doit être unique.',
    )

    @api.depends('name', 'year', 'host_country')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.year} - {record.host_country or record.name}"
