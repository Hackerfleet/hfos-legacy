ComponentConfigSchemaTemplate = {
    'type': 'object',
    'id': '#component',
    'name': 'component',
    'additionalproperties': True,
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Component ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name', 'description': 'Name of '
                                                                   'Component', 'default': 'NONAME'},
        'creator': {'type': 'string', 'title': 'Creator', 'description': 'Creator of Component'},
        'owneruuid': {'type': 'string', 'minLength': 36, 'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'color': {'type': 'string', 'format': 'color', 'title': 'Color of component',
                  'description': 'Background color of component'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Descriptive Component notes'},
        'componentclass': {'type': 'string', 'title': 'Component class', 'description': 'Type of component'},
        # 'settings': {
        #    'type': 'object',
        #    'oneOf': []
        # }
    },
    'default': {}
}

ComponentConfigForm = [
    '*'
]

ComponentBaseConfigSchema = {'schema': ComponentConfigSchemaTemplate,
                             'form': ComponentConfigForm}
