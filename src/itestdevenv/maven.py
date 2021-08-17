from xml.etree import ElementTree

default_namespace = 'http://maven.apache.org/POM/4.0.0'
ElementTree.register_namespace('', default_namespace)


def extract_version(file):
    tree = ElementTree.parse(file)
    ns_pref = '{' + default_namespace + '}'
    return tree.find(ns_pref + 'version').text

def remove_qualifier(version):
    return version.split('-')[0]
    
