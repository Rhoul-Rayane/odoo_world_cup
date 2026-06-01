from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WasteTracking(models.Model):
    _name = 'wc.waste.tracking'
    _description = 'Suivi des déchets'
    _inherit = ['mail.thread']
    _order = 'date desc, stadium_id'

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
    zone_id = fields.Many2one(
        'wc.stadium.zone',
        string='Zone',
        domain="[('stadium_id', '=', stadium_id)]",
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    waste_type = fields.Selection(
        [
            ('organic', 'Organique'),
            ('plastic', 'Plastique'),
            ('paper', 'Papier/Carton'),
            ('glass', 'Verre'),
            ('metal', 'Métal'),
            ('electronic', 'Électronique'),
            ('mixed', 'Déchets mélangés'),
        ],
        string='Type de déchet',
        required=True,
        tracking=True,
    )
    quantity_kg = fields.Float(
        string='Quantité (kg)',
        required=True,
    )
    recycled_kg = fields.Float(
        string='Quantité recyclée (kg)',
    )
    diverted_kg = fields.Float(
        string='Détourné de décharge (kg)',
    )
    diversion_rate = fields.Float(
        string='Taux de détournement (%)',
        compute='_compute_diversion_rate',
        store=True,
    )
    collector_company = fields.Char(
        string='Entreprise collectrice',
    )
    notes = fields.Text(
        string='Notes',
    )
    match_id = fields.Many2one(
        'wc.match',
        string='Match associé',
    )
    state = fields.Selection(
        [
            ('draft', 'Brouillon'),
            ('confirmed', 'Confirmé'),
            ('validated', 'Validé'),
        ],
        string='État',
        default='draft',
        tracking=True,
    )

    @api.depends('stadium_id.name', 'date', 'waste_type')
    def _compute_name(self):
        waste_type_labels = dict(self._fields['waste_type'].selection)
        for record in self:
            stadium_name = record.stadium_id.name or '?'
            date_str = record.date.strftime('%d/%m/%Y') if record.date else '?'
            type_label = waste_type_labels.get(record.waste_type, '?')
            record.name = f"{stadium_name} - {type_label} - {date_str}"

    @api.depends('quantity_kg', 'recycled_kg', 'diverted_kg')
    def _compute_diversion_rate(self):
        for record in self:
            if record.quantity_kg > 0:
                record.diversion_rate = (
                    (record.recycled_kg + record.diverted_kg) / record.quantity_kg * 100
                )
            else:
                record.diversion_rate = 0.0

    @api.constrains('quantity_kg')
    def _check_quantity_positive(self):
        for record in self:
            if record.quantity_kg <= 0:
                raise ValidationError(
                    "La quantité de déchets doit être strictement positive."
                )

    @api.constrains('recycled_kg', 'diverted_kg', 'quantity_kg')
    def _check_recycled_diverted(self):
        for record in self:
            if (record.recycled_kg + record.diverted_kg) > record.quantity_kg:
                raise ValidationError(
                    "La somme des quantités recyclées et détournées ne peut pas "
                    "dépasser la quantité totale de déchets."
                )

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_validate(self):
        for record in self:
            record.state = 'validated'
