from odoo import models, fields

class Incident(models.Model):
    _inherit = 'wc.logistics.incident'

    intervention_force_required = fields.Boolean(string="Intervention sur place requise", default=False)
    police_informed = fields.Boolean(string="Police nationale notifiée", default=False)
    drone_intercepted = fields.Boolean(string="Incident Drone", default=False)
    
    security_deployment_id = fields.Many2one(
        'wc.security.deployment', 
        string='Déploiement de sécurité lié',
        ondelete='set null'
    )
