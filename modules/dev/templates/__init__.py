import pystache
#from pprint import pprint


def format_template(template, content):
    result = u""
    if True:  # try:
        result = pystache.render(template, content, string_encoding='utf-8')
    # except (ValueError, KeyError) as e:
    #    print("Templating error: %s %s" % (e, type(e)))

    # pprint(result)
    return result


def format_template_file(filename, content):
    with open(filename, 'r') as f:
        template = f.read().decode('utf-8')

    return format_template(template, content)


def write_template_file(source, target, content):
    # print(formatTemplateFile(source, content))
    print(target)
    data = format_template_file(source, content)
    with open(target, 'w') as f:
        for line in data:
            f.write(line.encode('utf-8'))
