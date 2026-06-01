from odoo import models, fields

class Stadium(models.Model):
    _inherit = 'wc.stadium'

    country = fields.Selection(selection_add=[
        ('uruguay', 'Uruguay'),
        ('italy', 'Italie'),
        ('france', 'France'),
        ('brazil', 'Brésil'),
        ('switzerland', 'Suisse'),
        ('sweden', 'Suède'),
        ('chile', 'Chili'),
        ('england', 'Angleterre'),
        ('mexico', 'Mexique'),
        ('germany', 'Allemagne'),
        ('argentina', 'Argentine'),
        ('usa', 'États-Unis'),
        ('korea', 'Corée du Sud'),
        ('japan', 'Japon'),
        ('south_africa', 'Afrique du Sud'),
        ('russia', 'Russie'),
        ('qatar', 'Qatar'),
        ('other', 'Autre'),
    ], ondelete={
        'uruguay': 'set default',
        'italy': 'set default',
        'france': 'set default',
        'brazil': 'set default',
        'switzerland': 'set default',
        'sweden': 'set default',
        'chile': 'set default',
        'england': 'set default',
        'mexico': 'set default',
        'germany': 'set default',
        'argentina': 'set default',
        'usa': 'set default',
        'korea': 'set default',
        'japan': 'set default',
        'south_africa': 'set default',
        'russia': 'set default',
        'qatar': 'set default',
        'other': 'set default',
    })

    gps_lat = fields.Float(string='Latitude GPS', digits=(9, 6))
    gps_lng = fields.Float(string='Longitude GPS', digits=(9, 6))
    fifa_code = fields.Char(string='Code FIFA Stade', size=3, index=True)

    _fifa_code_uniq = models.Constraint(
        'unique(fifa_code)',
        'Le code FIFA du stade doit être unique.',
    )
