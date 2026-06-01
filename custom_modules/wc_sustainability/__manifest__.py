{
    'name': 'World Cup 2030 - Durabilité',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Suivi environnemental et audits ISO 20121 pour la Coupe du Monde 2030',
    'description': '''
World Cup 2030 - Module Durabilité
===================================

Ce module permet le suivi environnemental complet de la Coupe du Monde 2030 :

* **Suivi des déchets** : traçabilité par stade, type de déchet, taux de détournement
* **Empreinte carbone** : suivi des émissions CO₂ et compensations par catégorie
* **Audits ISO 20121** : conformité aux normes de développement durable événementiel

Fonctionnalités clés :
- Tableaux de bord visuels avec indicateurs de performance
- Workflow de validation des données environnementales
- Calcul automatique des taux de recyclage et émissions nettes
- Suivi de conformité ISO 20121 avec scoring et alertes
    ''',
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/waste_views.xml',
        'views/carbon_views.xml',
        'views/audit_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 7,
}
