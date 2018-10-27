"""
Sets up an ejabberd server for isomer chat operation
"""

import click
from click_didyoumean import DYMGroup
from warmongo import model_factory

from hfos.logger import hfoslog, debug, error
from hfos.misc import std_uuid
from hfos.tool import _check_root
from hfos.tool.misc import run_process


def log(*args, **kwargs):
    kwargs.update({'emitter': 'XMPPSetup', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


@click.group(cls=DYMGroup)
@click.pass_context
def xmpp(ctx):
    """Hello world"""

    _check_root()

    from hfos import database
    database.initialize(ctx.obj['dbhost'], ctx.obj['dbname'])

    from hfos.schemata.component import ComponentConfigSchemaTemplate
    factory = model_factory(ComponentConfigSchemaTemplate)
    bot_config = factory.find_one({'name': 'XMPPBOT'})

    if bot_config is None:
        password = std_uuid()

        bot_config = factory({
            'nick': 'claptrap',
            'name': 'XMPPBOT',
            'componentclass': 'XMPPBot',
            'jid': 'claptrap@localhost/node',
            'password': password,
            'uuid': std_uuid()
        })
        bot_config.save()

    # log(bot_config.serializablefields(), pretty=True)
    ctx.obj['bot_config'] = bot_config


@xmpp.command()
@click.pass_context
def add_system_user(ctx):
    bot_config = ctx.obj['bot_config']

    add_user = [
        'ejabberdctl',
        'register',
        bot_config.get('nick'),
        'localhost',
        bot_config.get('password')
    ]

    result = run_process('.', add_user)
    if b'conflict' in result:
        log('User already existing, updating password')
        update_password = [
            'ejabberdctl',
            'change_password',
            bot_config.get('nick'),
            'localhost',
            bot_config.get('password')
        ]
        result = run_process('.', update_password)
        if result != b'':
            log('Something problematic happened:', result)
    log('Done')


@xmpp.command()
def install(ctx):
    install_server = [
        'sudo',
        'apt-get',
        'install',
        'ejabberd'
    ]

    result = run_process('.', install_server)
    log('Done')
