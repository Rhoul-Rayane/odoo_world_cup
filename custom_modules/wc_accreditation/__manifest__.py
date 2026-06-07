{
    'name': 'World Cup 2030 - Accréditations',
    'version': '19.0.1.0.0',
    'category': 'Sports/Event Management',
    'summary': 'Gestion des badges et accréditations pour la Coupe du Monde 2030',
    'description': """
        Module de gestion des accréditations :
        - Badges numériques avec QR code
        - Catégories (FIFA, Média, Volontaire, VIP...)
        - Zones d'accès autorisées
        - Workflow d'approbation
        - Génération et vérification QR code
    """,
    'author': 'RHOUL Rayane - ENSAO/MGSI',
    'license': 'LGPL-3',
    'depends': ['wc_base', 'wc_volunteer', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/accreditation_test_data.xml',
        'views/accreditation_report.xml',
        'views/accreditation_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 3,
}
