from odoo import models, fields

class TransportStation(models.Model):
    _name = 'wc.transport.station'
    _description = 'Station de Transport'
    _order = 'name'

    name = fields.Char(string='Nom de la station', required=True)
    code = fields.Char(string='Code de la station', required=True, size=5, index=True)
    gps_lat = fields.Float(string='Latitude GPS', digits=(9, 6))
    gps_lng = fields.Float(string='Longitude GPS', digits=(9, 6))
    stadium_id = fields.Many2one('wc.stadium', string='Stade desservi', ondelete='set null')
    
    line_ids = fields.Many2many(
        'wc.transport.line', 
        'wc_transport_line_station_rel', 
        'station_id', 
        'line_id', 
        string='Lignes de transport'
    )

    _code_uniq = models.Constraint(
        'unique(code)',
        'Le code de la station doit être unique.',
    )
