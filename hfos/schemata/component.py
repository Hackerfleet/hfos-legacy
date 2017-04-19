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
            'description': 'HIDDEN'
        },
        'name': {
            'type': 'string',
            'title': 'Name',
            'description': 'Name of '
                           'Component',
            'default': 'NONAME'
        },
        'creator': {
            'type': 'string',
            'title': 'Creator',
            'description': 'Creator of Component'
        },
        'owner': {
            'type': 'string',
            'minLength': 36,
            'title': "Owner's Unique ID",
            'description': 'HIDDEN'
        },
        'color': {
            'type': 'string',  # 'format': 'color',
            'title': 'Color of component',
            'description': 'Background color of component'
        },
        'notes': {
            'type': 'string',
            'format': 'html',
            'title': 'User notes',
            'description': 'Descriptive Component notes'
        },
        'active': {
            'type': 'boolean',
            'title': 'Active',
            'default': True
        },
        'componentclass': {
            'type': 'string',
            'title': 'Component class',
            'description': 'Type of component'
        },
    }
}

ComponentConfigForm = [
    '*'
]

ComponentBaseConfigSchema = {'schema': ComponentConfigSchemaTemplate,
                             'form': ComponentConfigForm}
