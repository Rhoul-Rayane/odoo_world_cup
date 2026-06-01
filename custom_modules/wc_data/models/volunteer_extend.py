from odoo import models, fields

class Volunteer(models.Model):
    _inherit = 'wc.volunteer'

    functional_area = fields.Selection([
        ('accreditation', 'Accréditation'),
        ('media', 'Média & Presse'),
        ('ticketing', 'Billetterie'),
        ('transport', 'Transport & Logistique'),
        ('medical', 'Services Médicaux'),
        ('security', 'Sécurité & Gestion de Foule'),
        ('protocol', 'Protocole & VIP'),
    ], string='Secteur fonctionnel')

    training_level = fields.Selection([
        ('none', 'Non formé'),
        ('basic', 'Formation de base'),
        ('advanced', 'Formation avancée / Chef d\'équipe'),
    ], string='Niveau de formation', default='none')

    hours_worked = fields.Integer(string='Heures effectuées', default=0)
    attendance_rate = fields.Float(string='Taux de présence (%)', default=100.0)
