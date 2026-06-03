from odoo import models, fields, api


class Stadium(models.Model):
    _name = 'wc.stadium'
    _description = 'Stade - Coupe du Monde 2030'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom du stade', required=True, tracking=True)
    city = fields.Char(string='Ville', required=True, tracking=True)
    capacity = fields.Integer(string='Capacité', required=True, tracking=True)
    gross_capacity = fields.Integer(string='Capacité brute')
    net_capacity = fields.Integer(string='Capacité nette')
    address = fields.Text(string='Adresse')
    image = fields.Binary(string='Photo du stade', attachment=True)
    stadium_type = fields.Selection([
        ('match', 'Stade de Match (FIFA Official)'),
        ('training', 'Site d\'entraînement / Camp de base'),
    ], string='Usage du stade', default='match', required=True, tracking=True)
    state = fields.Selection([
        ('construction', 'En construction'),
        ('ready', 'Prêt'),
        ('maintenance', 'En maintenance'),
    ], string='Statut', default='construction', tracking=True)
    country = fields.Selection([
        ('morocco', 'Maroc'),
        ('spain', 'Espagne'),
        ('portugal', 'Portugal'),
    ], string='Pays', default='morocco', required=True)

    # Relations
    zone_ids = fields.One2many('wc.stadium.zone', 'stadium_id', string='Zones')
    match_ids = fields.One2many('wc.match', 'stadium_id', string='Matchs')

    # Champs calculés
    zone_count = fields.Integer(string='Nombre de zones', compute='_compute_zone_count')
    match_count = fields.Integer(string='Nombre de matchs', compute='_compute_match_count')
    active = fields.Boolean(default=True)

    @api.depends('zone_ids')
    def _compute_zone_count(self):
        for record in self:
            record.zone_count = len(record.zone_ids)

    @api.depends('match_ids')
    def _compute_match_count(self):
        for record in self:
            record.match_count = len(record.match_ids)

    def action_set_ready(self):
        self.write({'state': 'ready'})

    def action_set_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_view_zones(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Zones',
            'res_model': 'wc.stadium.zone',
            'view_mode': 'list,form',
            'domain': [('stadium_id', '=', self.id)],
            'context': {'default_stadium_id': self.id},
        }

    def action_view_matches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Matchs',
            'res_model': 'wc.match',
            'view_mode': 'list,form',
            'domain': [('stadium_id', '=', self.id)],
            'context': {'default_stadium_id': self.id},
        }
