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


