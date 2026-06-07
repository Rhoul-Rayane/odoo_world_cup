{
    'name': 'World Cup 2030 - Volontaires',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Gestion des volontaires pour la Coupe du Monde 2030',
    'description': """
        Module de gestion du capital humain bénévole :
        - Recrutement et pipeline de candidatures
        - Profil de compétences et langues
        - Algorithme de matching/scoring
        - Affectation par stade et zone
        - Gamification (badges, points)
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/volunteer_data.xml',
        'data/volunteer_test_records.xml',
        'views/volunteer_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 2,
}
