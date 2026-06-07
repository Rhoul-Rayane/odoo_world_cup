{
    'name': 'World Cup 2030 - Base',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Modèles de base pour la gestion de la Coupe du Monde 2030',
    'description': """
        Module de base contenant les modèles fondamentaux :
        - Stades
        - Zones de stade
        - Matchs
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/match_views.xml',
        'views/stadium_zone_views.xml',
        'views/stadium_views.xml',
        'views/menu_views.xml',
        'data/stadium_data.xml',
        'data/demo_users.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
