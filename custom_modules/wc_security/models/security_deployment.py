from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SecurityDeployment(models.Model):
    _name = 'wc.security.deployment'
    _description = 'Déploiement Sécurité Match'
    _order = 'match_id, stadium_zone_id'

    name = fields.Char(string='Référence', compute='_compute_name', store=True)
    match_id = fields.Many2one('wc.match', string='Match', required=True, ondelete='cascade')
    match_stadium_id = fields.Many2one('wc.stadium', related='match_id.stadium_id', readonly=True)
    
    stadium_zone_id = fields.Many2one(
        'wc.stadium.zone', 
        string='Zone du stade', 
        required=True, 
        domain="[('stadium_id', '=', match_stadium_id)]"
    )
    
    agent_count = fields.Integer(string="Nombre d'agents", required=True, default=10)
    supervisor_id = fields.Many2one('res.users', string='Superviseur', default=lambda self: self.env.user)
    
    deployment_type = fields.Selection([
        ('steward', 'Stewards / Accueil'),
        ('police', 'Forces de l\'ordre'),
        ('private', 'Sécurité privée'),
        ('medical', 'Secouristes / Médical'),
    ], string='Type de force', required=True, default='steward')

    @api.depends('match_id', 'stadium_zone_id', 'deployment_type')
    def _compute_name(self):
        for record in self:
            if record.match_id and record.stadium_zone_id and record.deployment_type:
                zone_name = record.stadium_zone_id.name
                type_label = dict(self._fields['deployment_type'].selection).get(record.deployment_type, record.deployment_type)
                record.name = f"SEC-{record.match_id.name} ({zone_name}) - {type_label}"
            else:
                record.name = "Nouveau déploiement"

    @api.constrains('agent_count')
    def _check_agent_count(self):
        for record in self:
            if record.agent_count <= 0:
                raise ValidationError("Le nombre d'agents de sécurité déployés doit être strictement supérieur à zéro.")
