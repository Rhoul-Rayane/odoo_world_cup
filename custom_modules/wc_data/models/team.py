from odoo import models, fields, api

class Team(models.Model):
    _name = 'wc.team'
    _description = 'Équipe Nationale'
    _order = 'name'

    name = fields.Char(string='Nom du pays', required=True)
    code_fifa = fields.Char(string='Code FIFA', required=True, size=3, index=True)
    confederation = fields.Selection([
        ('CAF', 'Afrique (CAF)'),
        ('UEFA', 'Europe (UEFA)'),
        ('CONMEBOL', 'Amérique du Sud (CONMEBOL)'),
        ('CONCACAF', 'Amérique du Nord/Centrale (CONCACAF)'),
        ('AFC', 'Asie (AFC)'),
        ('OFC', 'Océanie (OFC)'),
    ], string='Confédération')
    fifa_ranking = fields.Integer(string='Classement FIFA')
    lpi_score = fields.Float(string='Score LPI (World Bank)', digits=(4, 2),
                             help='World Bank Logistics Performance Index Score')
    lpi_rank = fields.Integer(string='Rang LPI (World Bank)')

    _code_uniq = models.Constraint(
        'unique(code_fifa)',
        'Le code FIFA doit être unique.',
    )

    @api.depends('name', 'code_fifa')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.code_fifa})"
