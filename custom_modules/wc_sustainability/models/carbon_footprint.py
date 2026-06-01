from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CarbonFootprint(models.Model):
    _name = 'wc.carbon.footprint'
    _description = 'Empreinte carbone'
    _inherit = ['mail.thread']
    _order = 'period_start desc'

    name = fields.Char(
        string='Référence',
        compute='_compute_name',
        store=True,
    )
    stadium_id = fields.Many2one(
        'wc.stadium',
        string='Stade',
        required=True,
        tracking=True,
    )
    period_start = fields.Date(
        string='Début de période',
        required=True,
    )
    period_end = fields.Date(
        string='Fin de période',
        required=True,
    )
    category = fields.Selection(
        [
            ('energy', 'Énergie & Électricité'),
            ('transport', 'Transport & Déplacements'),
            ('construction', 'Construction & Rénovation'),
            ('catering', 'Restauration'),
            ('waste', 'Gestion des déchets'),
            ('water', "Consommation d'eau"),
            ('other', 'Autre'),
        ],
        string='Catégorie',
        required=True,
        tracking=True,
    )
    emission_tons_co2 = fields.Float(
        string='Émissions (t CO₂)',
        required=True,
    )
    offset_tons_co2 = fields.Float(
        string='Compensations (t CO₂)',
        default=0,
    )
    net_emission = fields.Float(
        string='Émissions nettes (t CO₂)',
        compute='_compute_net_emission',
        store=True,
    )
    offset_method = fields.Char(
        string='Méthode de compensation',
    )
    data_source = fields.Char(
        string='Source des données',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('stadium_id.name', 'category', 'period_start')
    def _compute_name(self):
        category_labels = dict(self._fields['category'].selection)
        for record in self:
            stadium_name = record.stadium_id.name or '?'
            cat_label = category_labels.get(record.category, '?')
            date_str = record.period_start.strftime('%m/%Y') if record.period_start else '?'
            record.name = f"{stadium_name} - {cat_label} - {date_str}"

    @api.depends('emission_tons_co2', 'offset_tons_co2')
    def _compute_net_emission(self):
        for record in self:
            record.net_emission = record.emission_tons_co2 - record.offset_tons_co2

    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        for record in self:
            if record.period_end and record.period_start and record.period_end < record.period_start:
                raise ValidationError(
                    "La date de fin de période doit être postérieure ou égale "
                    "à la date de début."
                )

    @api.constrains('emission_tons_co2')
    def _check_emission_positive(self):
        for record in self:
            if record.emission_tons_co2 < 0:
                raise ValidationError(
                    "Les émissions de CO₂ ne peuvent pas être négatives."
                )
