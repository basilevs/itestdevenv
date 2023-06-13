from pathlib import Path
from os import walk
from xml.etree import ElementTree


def find_features(directory):
	for root, dirs, files in walk(directory):
		for file in files:
			if file == 'feature.xml':
				yield Path(root) / file

def remove_update_site(feature_xml):
	tree_builder = ElementTree.TreeBuilder(insert_pis=True, insert_comments=True)
	tree = ElementTree.parse(feature_xml, parser=ElementTree.XMLParser(target=tree_builder))
	element = tree.getroot().find('url')
	if element:
		tree.getroot().remove(element)
		with open(feature_xml, mode='w', encoding='utf-8') as f:
			f.write(serialize_tree(tree))


def serialize_tree(tree):
	text = ElementTree.tostring(tree.getroot(), encoding='unicode')
	text = text.replace(' />', '/>')
	text = '<?xml version="1.0" encoding="UTF-8"?>\n' + text + '\n'
	return text


for feature_file in find_features('my/source/directory'):
	remove_update_site(feature_file)