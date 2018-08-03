from hfos.tool.create_module import create_module
from hfos.tool.configuration import config
from hfos.tool.backup import db_export, db_import
from hfos.tool.database import db
from hfos.tool.objects import objects
from hfos.tool.installer import install, uninstall, update
from hfos.tool.rbac import rbac
from hfos.tool.user import user
from hfos.tool.misc import cmdmap, shell
from hfos.tool.cli import cli
from hfos.launcher import launch

cli.add_command(create_module)
cli.add_command(update)
cli.add_command(config)
cli.add_command(install)
cli.add_command(uninstall)
cli.add_command(cmdmap)
cli.add_command(shell)

db.add_command(user)
db.add_command(rbac)
db.add_command(objects)
db.add_command(db_export)
db.add_command(db_import)

cli.add_command(db)

cli.add_command(launch)

isotool = cli
