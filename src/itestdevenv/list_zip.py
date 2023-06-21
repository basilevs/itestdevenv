from concurrent.futures import ThreadPoolExecutor
from itertools import chain, product
from sys import argv
from requests import head
from zipfile import ZipFile
from os import walk
from pathlib import Path
from re import compile
from urllib.parse import urlparse, urljoin
from tempfile import TemporaryFile
from posixpath import basename

from .download import download_file


def list_zip(file):
	with ZipFile(file) as zip_file:
				error = zip_file.testzip()
				if error:
					raise ValueError("Failed to unzip {0}: {1}".format(file, error))
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

def list_url(url):
	with TemporaryFile() as temp_file:
		if url.scheme != 'file':
			download_file(url.geturl(), temp_file)
			temp_file.flush()
			temp_file.seek(0)
		else:
			temp_file = Path(url.path)
		out_file = basename(url.path) + '.txt'
		print('Product:', url.geturl(), out_file)	
		with open(out_file, 'w') as f:
			print('Product:', url.geturl(), file=f)
			for name in list_zip(temp_file):
				print(remove_version_from_name(name), file=f)

def consume(iterator):
	for _ in iterator:
		pass

def list_urls(urls):
	with ThreadPoolExecutor(max_workers=5) as executor:
		try:
			consume(executor.map(ensure_url_exists, urls))
			consume(executor.map(list_url, urls))
		finally:
			executor.shutdown(wait=False, cancel_futures=True)


def ensure_url_exists(url):
	head(url.geturl()).raise_for_status()


def list_all_products(build_artifact_directory_url):
	""" @param build_artifact_directory_url: URL to a directory containing
		zip files with build artifacts. The directory can be local or remote."""
	
	fully_supported_platforms = ['linux.gtk.x86_64.zip', 'win32.win32.x86_64.zip']
	all_platforms =  fully_supported_platforms + ['macosx.cocoa.aarch64.zip']
	products = map("-".join, chain(
		product(['iTest'], all_platforms), 
		product(['velocity-agent', 'iTestRT', 'ndo'], fully_supported_platforms)))
	urls = [urlparse(urljoin(build_artifact_directory_url, product)) for product in products]
	list_urls(urls)

if '__main__' == __name__:
	list_urls([urlparse(zip_file) for zip_file in argv[1:]])
