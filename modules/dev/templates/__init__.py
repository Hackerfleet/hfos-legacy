import pystache
from pprint import pprint


def formatTemplate(template, content):
    result = u""
    if True:  # try:
        result = pystache.render(template, content, string_encoding='utf-8')
    # except (ValueError, KeyError) as e:
    #    print("Templating error: %s %s" % (e, type(e)))

    # pprint(result)
    return result


def formatTemplateFile(filename, content):
    with open(filename, 'r') as f:
        template = f.read().decode('utf-8')

    return formatTemplate(template, content)


def writeTemplateFile(source, target, content):
    # print(formatTemplateFile(source, content))
    print(target)
    data = formatTemplateFile(source, content)
    with open(target, 'w') as f:
        for line in data:
            f.write(line.encode('utf-8'))
