{
    'name': 'World Cup 2030 - Logistique',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Gestion logistique multi-stades pour la Coupe du Monde 2030',
    'description': """
        Module de gestion logistique événementielle :
        - Ressources matérielles par stade et par zone
        - Demandes de ressources liées aux matchs
        - Transport et navettes inter-stades
        - Incidents et signalements temps réel
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'mail', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/logistics_data.xml',
        'views/resource_views.xml',
        'views/request_views.xml',
        'views/transport_views.xml',
        'views/incident_views.xml',
        'views/stadium_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 4,
}
