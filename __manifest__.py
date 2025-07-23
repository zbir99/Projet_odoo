{
    'name': 'Cabinet Medical',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Gestion de Cabinet Medical',
    'description': """
        Module de gestion pour cabinet médical incluant:
        - Gestion des patients
        - Gestion des rendez-vous
        - Gestion des consultations
        - Gestion des médecins
        - Génération d'ordonnances
        - Tableau de bord et statistiques
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'calendar',
        'sale',
        'purchase',
        'stock',
        'account',
        'web',
    ],
    'data': [
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'views/patient_views.xml',
        'views/medecin_views.xml',
        'views/consultation_views.xml',
        'views/rendez_vous_views.xml',
        'views/facture_views.xml',
        'views/paiement_views.xml',
        'views/menu_views.xml',
        'views/dashboard_views.xml',
        'wizard/wizard_views.xml',
        'report/medical_reports.xml',
        'report/facture_report_template.xml',
        'data/sequence_data.xml',
        'data/account_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    # Temporairement désactivé pour résoudre le problème de page blanche
    # 'assets': {
    #     'web.assets_backend': [
    #         ('include', 'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js'),
    #         'cabinet_medecin/static/src/js/dashboard.js',
    #     ],
    #     'web.assets_qweb': [
    #         'cabinet_medecin/static/src/xml/dashboard.xml',
    #     ],
    # },
}
