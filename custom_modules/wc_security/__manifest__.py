{
    'name': 'World Cup 2030 - Sécurité & Crowd Management',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Gestion de la sécurité des stades, accords internationaux et monitoring des foules',
    'description': """
        Module de sécurité et de gestion de foule pour la Coupe du Monde 2030 :
        - Déploiement des effectifs de sécurité par match et zone
        - Accords de sécurité internationaux (coopération de police, cybersécurité, anti-drone)
        - Monitoring de la densité de foule en temps réel avec indicateurs couleur de niveau d'alerte
        - Extension des incidents logistiques pour la sécurité (besoin d'intervention, drone)
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'wc_logistics', 'wc_data'],
    'data': [
        'security/ir.model.access.csv',
        'data/security_data.xml',
        'views/security_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 8,
}
