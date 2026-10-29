{
    'name': 'Real Estate',
    'version': '1.0',
    'depends': ['base'],
    'author': 'Your Name',
    'category': 'Real Estate/Brokerage',
    'description': 'A complete real estate management module.',
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}