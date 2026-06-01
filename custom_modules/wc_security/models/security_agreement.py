from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SecurityAgreement(models.Model):
    _name = 'wc.security.agreement'
    _description = 'Accord International de Sécurité'
    _order = 'effective_date desc'

    name = fields.Char(string="Nom de l'accord", required=True)
    partner_country = fields.Selection([
        ('france', 'France'),
        ('spain', 'Espagne'),
        ('portugal', 'Portugal'),
        ('usa', 'États-Unis'),
        ('uk', 'Royaume-Uni'),
        ('turkey', 'Turquie'),
        ('qatar', 'Qatar'),
        ('saudi_arabia', 'Arabie Saoudite'),
        ('other', 'Autre'),
    ], string='Pays partenaire', required=True)
    
    agreement_type = fields.Selection([
        ('personnel', 'Mise à disposition de forces / police'),
        ('cybersecurity', 'Cybersécurité & Renseignement'),
        ('anti_drone', 'Lutte anti-drone'),
        ('crowd_control', 'Gestion des foules & Tactique'),
        ('training', 'Formation & Exercices'),
    ], string="Type d'accord", required=True, default='personnel')
    
    effective_date = fields.Date(string="Date d'effet", required=True, default=fields.Date.context_today)
    expiration_date = fields.Date(string="Date d'expiration")
    personnel_deployed = fields.Integer(string="Personnel déployé (estimé)", default=0)
    description = fields.Text(string="Détails de l'accord")

    @api.constrains('effective_date', 'expiration_date', 'personnel_deployed')
    def _check_dates(self):
        for record in self:
            if record.effective_date and record.expiration_date and record.expiration_date < record.effective_date:
                raise ValidationError("La date d'expiration ne peut pas être antérieure à la date d'effet de l'accord.")
            if record.personnel_deployed < 0:
                raise ValidationError("Le personnel déployé ne peut pas être négatif.")
