from concurrent.futures import ThreadPoolExecutor
from sys import argv
from zipfile import ZipFile
from os import walk
from pathlib import Path
from re import compile
from urllib.parse import urlparse
from tempfile import TemporaryFile

from .download import download_file


def list_zip(file):
	with ZipFile(file) as zip_file:
				error = zip_file.testzip()
				if error:
					raise ValueError("Failed to unzip {0}: {1}".format(url, error))
				return zip_file.namelist()

version_pattern = compile(r'\d+\.\d+\.\d+.\d+|\d{4,13}')


def remove_version_from_name(name):
	 # nda/plugins/javax.xml.rpc_1.1.0.v201209140446/META-INF/MANIFEST.MF
	 return version_pattern.sub('', name)

_exclude = set(['Python', 'extraArtifacts', 'repository', '-SNAPSHOT'])
def find_products(dir):
	for root, dirs, files in walk(dir):
		dirs[:] = [d for d in dirs if d not in _exclude]
		for file in files:
			if any(a in file for a in _exclude):
				continue
			if file.endswith('.zip'):
				yield Path(root) / file

def process_url(url):
	with TemporaryFile() as temp_file:
		if url.scheme != 'file':
			download_file(url.geturl(), temp_file)
			temp_file.flush()
			temp_file.seek(0)
		else:
			temp_file = Path(url.path)
		out_file = temp_file.name + '.txt'
		print('Product:', url, out_file)	
		with open(out_file, 'w') as f:
			print('Product:', url, file=f)
			for name in list_zip(temp_file):
				print(remove_version_from_name(name), file=f)

if '__main__' == __name__:
	with ThreadPoolExecutor(max_workers=10) as executor:
		futures = []
		for zip_file in argv[1:]:
			futures.append(executor.submit(process_url, urlparse(zip_file)))
		for future in futures:
			future.result()