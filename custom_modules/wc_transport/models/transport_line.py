from odoo import models, fields

class TransportLine(models.Model):
    _name = 'wc.transport.line'
    _description = 'Ligne de Transport'
    _order = 'name'

    name = fields.Char(string='Nom de la ligne', required=True)
    line_type = fields.Selection([
        ('metro', 'Métro'),
        ('bus', 'Bus (BRT)'),
        ('tram', 'Tramway'),
        ('train', 'Train (Al Boraq/RER)'),
    ], string='Type de transport', required=True, default='bus')
    capacity_per_hour = fields.Integer(string='Capacité passagers/heure', default=2000)
    color = fields.Char(string='Couleur UI', default='#000000', help="Couleur hexadécimale de la ligne")
    active = fields.Boolean(default=True)
    
    station_ids = fields.Many2many(
        'wc.transport.station', 
        'wc_transport_line_station_rel', 
        'line_id', 
        'station_id', 
        string='Stations'
    )
    schedule_ids = fields.One2many('wc.transport.schedule', 'line_id', string='Plannings')
