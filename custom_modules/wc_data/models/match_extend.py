from odoo import models, fields, api

class Match(models.Model):
    _inherit = 'wc.match'

    tournament_id = fields.Many2one('wc.tournament', string='Tournoi', ondelete='set null')
    team_a_id = fields.Many2one('wc.team', string='Équipe A (Réelle)', ondelete='set null')
    team_b_id = fields.Many2one('wc.team', string='Équipe B (Réelle)', ondelete='set null')
    is_historical = fields.Boolean(string='Match Historique', default=False)

    @api.onchange('team_a_id')
    def _onchange_team_a_id(self):
        if self.team_a_id:
            self.team_a = self.team_a_id.name

    @api.onchange('team_b_id')
    def _onchange_team_b_id(self):
        if self.team_b_id:
            self.team_b = self.team_b_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('team_a_id') and not vals.get('team_a'):
                team = self.env['wc.team'].browse(vals['team_a_id'])
                vals['team_a'] = team.name
            if vals.get('team_b_id') and not vals.get('team_b'):
                team = self.env['wc.team'].browse(vals['team_b_id'])
                vals['team_b'] = team.name
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('team_a_id') and not vals.get('team_a'):
            team = self.env['wc.team'].browse(vals['team_a_id'])
            vals['team_a'] = team.name
        if vals.get('team_b_id') and not vals.get('team_b'):
            team = self.env['wc.team'].browse(vals['team_b_id'])
            vals['team_b'] = team.name
        return super().write(vals)
