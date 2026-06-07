{
    'name': 'World Cup 2030 - Dashboard',
    'version': '19.0.2.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Tableau de bord décisionnel et KPIs pour la Coupe du Monde 2030',
    'description': """
        Module tableau de bord complet avec indicateurs clés :
        - Statistiques volontaires (pipeline, scores)
        - Suivi stades et matchs
        - Accréditations actives et expirées
        - Incidents logistiques par sévérité
        - Transport multimodal et parking
        - Sécurité et monitoring foule
        - Durabilité et empreinte carbone
        - Finance, budget et billetterie
        - Benchmarks Qatar 2022 intégrés
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': [
        'wc_base',
        'wc_volunteer',
        'wc_accreditation',
        'wc_logistics',
        'wc_security',
        'wc_sustainability',
        'wc_finance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'data/demo_test_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 5,
}
