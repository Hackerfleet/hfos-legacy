ComponentConfigSchemaTemplate = {
    'type': 'object',
    'id': '#component',
    'name': 'component',
    'additionalproperties': True,
    'properties': {
        'uuid': {
            'type': 'string',
            'minLength': 36,
            'title': 'Unique Component ID',
            'description': 'HIDDEN',
            'readonly': True,
            'x-schema-form': {
                'condition': "false"
            }
        },
        'name': {
            'type': 'string',
            'title': 'Name',
            'description': 'Name of '
                           'Component',
            'default': 'NONAME',
            'readonly': True
        },
        'creator': {
            'type': 'string',
            'title': 'Creator',
            'description': 'Creator of Component',
            'readonly': True,
            'x-schema-form': {
                'condition': "false"
            }
        },
        'owner': {
            'type': 'string',
            'minLength': 36,
            'title': "Owner's Unique ID",
            'description': 'HIDDEN',
            'readonly': True,
            'x-schema-form': {
                'condition': "false"
            }
        },
        'color': {
            'type': 'string',  # 'format': 'color',
            'title': 'Color of component',
            'description': 'Background color of component'
        },
        'notes': {
            'type': 'string',
            'format': 'html',
            'title': 'Description',
            'description': 'Descriptive Component notes',
            'readonly': True,
            'x-schema-form': {
                'type': 'textarea',
                'fieldHtmlClass': 'textlabel'
            }
        },
        'active': {
            'type': 'boolean',
            'title': 'Active',
            'default': True
        },
        'componentclass': {
            'type': 'string',
            'title': 'Component class',
            'description': 'Type of component',
            'readonly': True
        },
    }
}

ComponentConfigForm = [
    '*'
]

ComponentBaseConfigSchema = {'schema': ComponentConfigSchemaTemplate,
                             'form': ComponentConfigForm}
