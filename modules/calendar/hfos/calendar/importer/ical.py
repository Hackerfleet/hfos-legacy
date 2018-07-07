"""
Imports calendar entries from a given ics file.
"""

from icalendar import Calendar, Event
import datetime
from dateutil import parser
import click
from hfos.logger import hfoslog, warn, verbose, debug
from hfos.misc import std_uuid, std_now


def log(*args, **kwargs):
    kwargs.update({'emitter': 'ICALIMPORT', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


@click.command('icalimporter')
@click.argument('filename')
@click.option('--all', default=False, help='Import past calendar entries')
@click.option('--owner')
@click.option('--calendar')
@click.option('--create-calendar', is_flag=True, default=False)
@click.option('--clear-calendar', is_flag=True, default=False)
@click.option('--dry', is_flag=True, default=False)
@click.option('--execfilter', default=None)
@click.pass_context
def ICALImporter(ctx, filename, all, owner, calendar, create_calendar, clear_calendar, dry, execfilter):
    """Calendar Importer for iCal (ics) files

    """

    log('iCal importer running')

    objectmodels = ctx.obj['db'].objectmodels

    if objectmodels['user'].count({'name': owner}) > 0:
        owner_object = objectmodels['user'].find_one({'name': owner})
    elif objectmodels['user'].count({'uuid': owner}) > 0:
        owner_object = objectmodels['user'].find_one({'uuid': owner})
    else:
        log('User unknown. Specify either uuid or name.', lvl=warn)
        return

    log('Found user')

    if objectmodels['calendar'].count({'name': calendar}) > 0:
        calendar = objectmodels['calendar'].find_one({'name': calendar})
    elif objectmodels['calendar'].count({'uuid': owner}) > 0:
        calendar = objectmodels['calendar'].find_one({'uuid': calendar})
    elif create_calendar:
        calendar = objectmodels['calendar']({
            'uuid': std_uuid(),
            'name': calendar
        })
    else:
        log('Calendar unknown and no --create-calendar specified. Specify either uuid or name of an existing calendar.',
            lvl=warn)
        return

    log('Found calendar')

    if clear_calendar is True:
        log('Clearing calendar events')
        for item in objectmodels['event'].find({'calendar': calendar.uuid}):
            item.delete()

    with open(filename, 'rb') as file_object:
        caldata = Calendar.from_ical(file_object.read())

    keys = {
        'class': 'str',
        'created': 'dt',
        'description': 'str',
        'dtstart': 'dt',
        'dtend': 'dt',
        'timestamp': 'dt',
        'modified': 'dt',
        'location': 'str',
        'status': 'str',
        'summary': 'str',
        'uid': 'str'
    }
    mapping = {
        'description': 'summary',
        'summary': 'name'
    }

    imports = []

    def ical_import_filter(original, logfacilty):
        log('Passthrough filter')
        return original

    if execfilter is not None:
        import os

        textFilePath = os.path.abspath(os.path.join(os.path.curdir, execfilter))
        textFileFolder = os.path.dirname(textFilePath)

        from importlib.machinery import SourceFileLoader

        filter_module = SourceFileLoader("importfilter", textFilePath).load_module()
        ical_import_filter = filter_module.ical_import_filter

    for event in caldata.walk():
        if event.name == 'VEVENT':
            log(event, lvl=verbose, pretty=True)
            initializer = {
                'uuid': std_uuid(),
                'calendar': calendar.uuid,
            }

            for item in keys:
                thing = event.get(item, None)
                if thing is None:
                    thing = 'NO-' + item
                else:
                    if keys[item] == 'str':
                        thing = str(thing)
                    else:
                        thing = parser.parse(str(thing.dt))
                        thing = thing.isoformat()

                if item in mapping:
                    item_assignment = mapping[item]
                else:
                    item_assignment = item

                initializer[item_assignment] = thing
            new_event = objectmodels['event'](initializer)

            new_event = ical_import_filter(new_event, log)

            imports.append(new_event)

            log(new_event, lvl=debug)

    for ev in imports:
        log(ev.summary)

    if not dry:
        log('Bulk creating events')
        objectmodels['event'].bulk_create(imports)

        calendar.save()
    else:
        log('Dry run - nothing stored.', lvl=warn)
