#  @author: Michael Wagner
#  @organization: TU Dresden
#  @contact: michael.wagner@tu-dresden.de

import xml.etree.ElementTree as ElementTree
import re

et = ElementTree


def create_view(catalog_file, outfiles):
    # creation of a view for import in RDMO

    tree, ns = parse_and_get_ns(catalog_file)
    # tree = et.parse(catalog_file)
    root = tree.getroot()

    for lang in outfiles:
        # create a catalog for each language
        outfile = outfiles[lang]

        fid = open(outfile, "w")
        fid.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fid.write('<rdmo')
        # write namespaces
        for ns_act in ns:
            fid.write(' xmlns:' + ns_act + '="' + ns[ns_act] + '"')
        fid.write('>\n')

        uri_prefix = None
        dataset_collections_all = {}
        dataset_collections_shortnames = {}

        questionset_is_collection = None
        question_is_collection = None
        attribute_value = None
        template = str()

        for child in root:

            if child.tag == "catalog":
                # get catalog element

                catalog = child.attrib['{' + ns['dc'] + '}uri']
                uri_prefix = child.find("uri_prefix").text
                if uri_prefix[-1] == "/":
                    # remove trailing slash
                    uri_prefix = uri_prefix[0:-1]
                key = child.find("key").text
                try:
                    comment = child.find("comment").text
                except AttributeError:
                    comment = None
                title_dict = get_element_dict(child.findall("title"), lang)
                try:
                    help_dict = get_element_dict(child.findall("help"), lang)
                except AttributeError:
                    help_dict = None

                fid.write('  <view dc:uri="' + uri_prefix + '/views/' + key + '">\n')
                fid.write('    <uri_prefix>' + uri_prefix + '</uri_prefix>\n')
                fid.write('    <key>' + key + '</key>\n')
                if comment is not None:
                    fid.write('    <dc:comment>' + comment + '</comment>\n')
                else:
                    fid.write('    <dc:comment />\n')
                for title in title_dict:
                    fid.write('    <title lang="' + title + '">' + title_dict[title] + '</title>\n')
                for help_act in help_dict:
                    fid.write('    <help lang="' + help_act + '">' + help_dict[help_act] + '</help>\n')
                fid.write('    <catalogs>\n')
                fid.write('      <catalog dc:uri="' + catalog + '"/>\n')
                fid.write('    </catalogs>\n')

                fid.write('    <template>\n')
                template = template + "{% load view_tags %}\n\n"
                template = template + '  <h1>' + title_dict[lang] + '</h1>\n'

            elif child.tag == "section":
                # get section element

                title_dict = get_element_dict(child.findall("title"), lang)

                template = template + "\n"
                template = template + '  <h2>' + title_dict[lang] + '</h2>\n'

            elif child.tag == "questionset":
                # get questionset element

                title_dict = get_element_dict(child.findall("title"), lang)
                help_dict = get_element_dict(child.findall("help"), lang)

                template = template + "\n"
                template = template + '  <h3>' + title_dict[lang] + '</h3>\n'
                if help_dict[lang] is not None:
                    template = template + '  <i>' + help_dict[lang] + '</i>\n'

                if child.find("is_collection").text.lower() == 'true':
                    questionset_is_collection = True
                    attribute = child.find("attribute").attrib
                    attribute_value = attribute['{' + ns['dc'] + '}uri']
                    if attribute_value not in dataset_collections_all:
                        attribute_shortname, attribute_shortnames, attribute_postfix = \
                            get_attribute_shortnames(attribute_value, uri_prefix)

                        template = template + "\n"
                        template = template + "{% get_set '" + attribute_postfix + "' as " + attribute_shortnames + ' %}\n'

                        dataset_collections_all[attribute_value] = attribute_shortnames
                        dataset_collections_shortnames[attribute_value] = attribute_shortname

                else:
                    questionset_is_collection = False

            if child.tag == "question":
                # get question element

                if child.find("is_collection").text.lower() == 'true':
                    question_is_collection = True

                question_attribute = child.find("attribute").attrib
                question_attribute_value = question_attribute['{' + ns['dc'] + '}uri']
                question_attribute_postfix = get_attribute_shortnames(question_attribute_value, uri_prefix)[2]

                text_dict = get_element_dict(child.findall("text"), lang)
                help_dict = get_element_dict(child.findall("help"), lang)

                template = template + "\n"
                template = template + '<p>\n'
                template = template + '  <br>\n'
                template = template + '  <b>' + text_dict[lang] + '</b>\n'
                if help_dict[lang] is not None:
                    template = template + '  <i>' + help_dict[lang] + '</i>\n'
                template = template + '</p>\n'

                if questionset_is_collection:
                    template = template + '{% for ' + dataset_collections_shortnames[attribute_value] + ' in ' + \
                                          dataset_collections_all[attribute_value] + ' %}\n'
                    template = template + '<p>\n'
                    template = template + '  <i>' + dataset_collections_shortnames[attribute_value] + ' {{ ' + \
                                          dataset_collections_shortnames[attribute_value] + '.value }}:</i>\n'
                    if question_is_collection:
                        template = template + '  {% render_set_value_list ' + dataset_collections_shortnames[
                            attribute_value] + " '" + question_attribute_postfix + "' %}\n"
                    else:
                        template = template + '  {% render_set_value ' + dataset_collections_shortnames[
                            attribute_value] + " '" + question_attribute_postfix + "' %}\n"
                    template = template + '</p>\n'
                    template = template + '{% endfor %}\n'
                else:
                    template = template + '<p>\n'
                    if question_is_collection:
                        template = template + "  {% render_value_list '" + question_attribute_postfix + "' %}\n"
                    else:
                        template = template + "  {% render_value '" + question_attribute_postfix + "' %}\n"
                    template = template + '</p>\n'

        # change template content to escaped xml content
        fid.write(escape_xml_characters(template))
        # fid.write(template)
        fid.write('    </template>\n')
        fid.write('  </view>\n')
        fid.write('</rdmo>\n')
        fid.close()


def get_element_dict(elements, lang):
    # produce a dictionary with language abbreviation and content

    element_dict = {}
    for element in elements:
        if element.attrib["lang"] in lang:
            element_dict[element.attrib["lang"]] = element.text

    return element_dict


def get_attribute_shortnames(attribute_value, uri_prefix):
    # get short names for attributes

    attribute_prefix = uri_prefix + "/domain/"
    attribute_postfix = attribute_value.replace(attribute_prefix, "")
    attribute_last = re.split('/', attribute_postfix)
    attribute_shortname = attribute_last[len(attribute_last) - 1]
    attribute_shortnames = attribute_last[len(attribute_last) - 1] + '_all'

    return attribute_shortname, attribute_shortnames, attribute_postfix


def parse_and_get_ns(file):
    # parse a xml file and get a dict of namespaces
    # taken from https://stackoverflow.com/questions/1953761/accessing-xmlns-attribute-with-python-elementree

    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in et.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #     to different URI namespaces in different parts of the
                #     document. This exception serves as a reminder that this
                #     solution is not robust. Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            if root is None:
                root = elem

    return et.ElementTree(root), ns


def escape_xml_characters(in_str):
    # replace xml control characters from string

    control_char = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;"
    }

    out_str = in_str
    for i in control_char:
        out_str = out_str.replace(i, control_char[i])

    return out_str


def control_create_view(infile, **outfiles):

    create_view(infile, outfiles)


def main():
    # infile = "infiles/example1_questions.xml"
    infile = "infiles/qa_questions.xml"

    # define languages of interest -> create view for each language
    control_create_view(infile, en="outfiles/qa_questions_view_template_en.xml")
    # control_create_view(infile, en="outfiles/example1_view_template_en.xml",
    #                     de="outfiles/example1_view_template_de.xml")


if __name__ == '__main__':
    main()
