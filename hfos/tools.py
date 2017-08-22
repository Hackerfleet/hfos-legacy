from datetime import datetime
from pprint import pprint
from uuid import uuid4


def std_now():
    return datetime.now().isoformat()


def std_uuid():
    return str(uuid4())


def std_table(rows):
    result = ""
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(len(max([x[i] for x in rows] + [headers[i]],
                                key=lambda x: len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        result += hpattern % tuple(headers) + " \n"
        result += separator + "\n"
        _u = lambda t: t if isinstance(t, str) else t
        for line in rows:
            result += pattern % tuple(_u(t) for t in line) + "\n"
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields, key=lambda x: len(x)))
        for i in range(len(row)):
            result += "%*s = %s" % (hwidth, row._fields[i], row[i]) + "\n"

    return result


def format_template(template, content):
    import pystache
    result = u""
    if True:  # try:
        result = pystache.render(template, content, string_encoding='utf-8')
    # except (ValueError, KeyError) as e:
    #    print("Templating error: %s %s" % (e, type(e)))

    # pprint(result)
    return result


def format_template_file(filename, content):
    with open(filename, 'r') as f:
        template = f.read()
        if type(template) != str:
            template = template.decode('utf-8')

    return format_template(template, content)


def write_template_file(source, target, content):
    # print(formatTemplateFile(source, content))
    print(target)
    data = format_template_file(source, content)
    with open(target, 'w') as f:
        for line in data:
            if type(line) != str:
                line = line.encode('utf-8')
            f.write(line)


def insert_nginx_service(definition):
    config_file = '/etc/nginx/sites-available/hfos.conf'
    splitter = "### SERVICE DEFINITIONS ###"

    with open(config_file, 'r') as f:
        old_config = "".join(f.readlines())

    pprint(old_config)

    if definition in old_config:
        print("Service definition already inserted")
        return

    parts = old_config.split(splitter)
    print(len(parts))
    if len(parts) != 3:
        print("Nginx configuration seems to be changed and cannot be "
              "extended automatically anymore!")
        pprint(parts)
        return

    try:
        with open(config_file, "w") as f:
            f.write(parts[0])
            f.write(splitter + "\n")
            f.write(parts[1])
            for line in definition:
                f.write(line)
            f.write("\n    " + splitter)
            f.write(parts[2])
    except Exception as e:
        print("Error during Nginx configuration extension:", type(e), e)