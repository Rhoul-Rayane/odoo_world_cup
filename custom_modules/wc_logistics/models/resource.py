from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LogisticsResource(models.Model):
    _name = 'wc.logistics.resource'
    _description = 'Ressource Logistique'
    _inherit = ['mail.thread']
    _order = 'category, name'

    name = fields.Char(string='Désignation', required=True, tracking=True)
    category = fields.Selection([
        ('furniture', 'Mobilier (chaises, tables, tentes)'),
        ('signage', 'Signalétique (panneaux, bannières)'),
        ('tech', 'Équipement technique (écrans, son)'),
        ('medical', 'Matériel médical'),
        ('security', 'Équipement sécurité'),
        ('cleaning', 'Matériel entretien'),
        ('catering', 'Restauration (frigos, fontaines)'),
        ('communication', 'Communication (talkies, radios)'),
    ], string='Catégorie', required=True, tracking=True)

    total_qty = fields.Integer(string='Quantité totale', required=True, default=1)
    available_qty = fields.Integer(string='Quantité disponible',
                                   compute='_compute_available_qty', store=True)
    unit = fields.Char(string='Unité', default='unité')

    stadium_id = fields.Many2one('wc.stadium', string='Stade de stockage', tracking=True)
    zone_id = fields.Many2one('wc.stadium.zone', string='Zone',
                              domain="[('stadium_id', '=', stadium_id)]")

    state = fields.Selection([
        ('available', 'Disponible'),
        ('low', 'Stock faible'),
        ('out', 'Rupture'),
    ], string='État', compute='_compute_state', store=True)

    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    # Relations
    request_line_ids = fields.One2many('wc.logistics.request.line', 'resource_id',
                                       string='Demandes liées')

    @api.depends('total_qty', 'request_line_ids', 'request_line_ids.state', 'request_line_ids.quantity')
    def _compute_available_qty(self):
        for record in self:
            reserved = sum(
                line.quantity for line in record.request_line_ids
                if line.state in ('approved', 'delivered')
            )
            record.available_qty = record.total_qty - reserved

    @api.depends('available_qty', 'total_qty')
    def _compute_state(self):
        for record in self:
            if record.available_qty <= 0:
                record.state = 'out'
            elif record.available_qty < (record.total_qty * 0.2):
                record.state = 'low'
            else:
                record.state = 'available'


class LogisticsRequestLine(models.Model):
    _name = 'wc.logistics.request.line'
    _description = 'Ligne de demande de ressource'

    request_id = fields.Many2one('wc.logistics.request', string='Demande',
                                  required=True, ondelete='cascade')
    resource_id = fields.Many2one('wc.logistics.resource', string='Ressource', required=True)
    quantity = fields.Integer(string='Quantité demandée', required=True, default=1)
    state = fields.Selection(related='request_id.state', string='État', store=True)
