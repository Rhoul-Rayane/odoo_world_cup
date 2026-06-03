{
    'name': 'World Cup 2030 - Données Réelles',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Données et modèles réels FIFA pour la Coupe du Monde 2030',
    'description': """
        Module d'intégration des données réelles de la FIFA :
        - Éditions historiques de la Coupe du Monde
        - Équipes nationales et classements FIFA
        - Index de performance logistique (LPI) par pays
        - Historique des matchs et statistiques
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'wc_volunteer', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/tournament_data.xml',
        'data/team_data.xml',
        'views/tournament_views.xml',
        'views/team_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 6,
}
