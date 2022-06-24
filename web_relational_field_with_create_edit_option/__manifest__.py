{
    'name': 'web_relational_field_with_create_edit_option',
    'version': '15.0.1.0.0.',
    'license': '',
    'author': "Quanam",
    'website': "https://www.quanam.com",
    'description': """
Adds create and edit options in relational field value list.

""",
    'depends': ['base', 'web'],
    "assets": {
        "web.assets_backend": [
            "web_relational_field_with_create_edit_option/static/src/js/relational_fields.js",
        ],
    },
}
