{
    'name': 'World Cup 2030 - Finance & Billetterie',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Gestion budgétaire, revenus et billetterie pour la Coupe du Monde 2030',
    'description': """
World Cup 2030 - Finance & Billetterie
=======================================

Module de gestion financière pour la Coupe du Monde FIFA 2030.

Fonctionnalités :
- **Budget analytique** : Suivi CAPEX/OPEX par stade et catégorie
- **Flux de revenus** : Billetterie, sponsoring, droits TV, merchandising
- **Grille tarifaire** : Prix par phase, catégorie, remises résidents/étudiants
- Tableaux de bord financiers avec taux de consommation et écarts
- Workflow de validation budgétaire et de facturation
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/budget_views.xml',
        'views/revenue_views.xml',
        'views/pricing_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 8,
}
