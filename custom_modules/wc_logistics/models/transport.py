from odoo import models, fields, api


class Transport(models.Model):
    _name = 'wc.logistics.transport'
    _description = 'Transport / Navette Inter-Stades'
    _inherit = ['mail.thread']
    _order = 'departure_time'

    name = fields.Char(string='Identifiant navette', required=True)
    vehicle_type = fields.Selection([
        ('bus', 'Bus'),
        ('minibus', 'Minibus'),
        ('van', 'Van'),
        ('car', 'Voiture'),
        ('ambulance', 'Ambulance'),
    ], string='Type de véhicule', required=True)

    capacity = fields.Integer(string='Capacité (passagers)', required=True)
    driver_name = fields.Char(string='Chauffeur')
    driver_phone = fields.Char(string='Tél. chauffeur')
    plate_number = fields.Char(string='Immatriculation')

    # Trajet
    origin_stadium_id = fields.Many2one('wc.stadium', string='Stade de départ', required=True)
    destination_stadium_id = fields.Many2one('wc.stadium', string='Stade d\'arrivée', required=True)
    departure_time = fields.Datetime(string='Heure de départ', required=True)
    arrival_time = fields.Datetime(string='Heure d\'arrivée estimée')
    match_id = fields.Many2one('wc.match', string='Match associé')

    passenger_count = fields.Integer(string='Passagers à bord', default=0)

    state = fields.Selection([
        ('planned', 'Planifié'),
        ('boarding', 'Embarquement'),
        ('transit', 'En route'),
        ('arrived', 'Arrivé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='planned', tracking=True)

    notes = fields.Text(string='Notes')

    def action_board(self):
        self.write({'state': 'boarding'})

    def action_depart(self):
        self.write({'state': 'transit'})

    def action_arrive(self):
        self.write({'state': 'arrived'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
