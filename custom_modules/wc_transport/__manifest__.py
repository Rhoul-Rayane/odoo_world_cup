{
    'name': 'World Cup 2030 - Transport Multimodal',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Gestion du transport multimodal et des navettes inter-stades',
    'description': """
        Module de gestion et de planification des transports pour la Coupe du Monde 2030 :
        - Lignes de transport (métro, bus, tram, train)
        - Stations de transport avec coordonnées GPS et liaison aux stades
        - Zones de parking (VIP, public, médias, staff)
        - Navettes renforcées et planification liées aux matchs
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'wc_data'],
    'data': [
        'security/ir.model.access.csv',
        'data/transport_data.xml',
        'views/transport_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 7,
}
