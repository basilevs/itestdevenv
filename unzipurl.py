#!/usr/bin/python3

from tempfile import TemporaryFile
from zipfile import ZipFile, ZipInfo
from os import chmod
from requests import get


class ZipFileWithPermissions(ZipFile):
    """ Custom ZipFile class handling file permissions. """
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            chmod(targetpath, attr)
        return targetpath



def unzip_url(url, dst_dir):
    with TemporaryFile() as temp_file:
        download_file(url, temp_file)
        temp_file.flush()
        with ZipFileWithPermissions(temp_file) as zip:
            error = zip.testzip()
            if error:
                raise ValueError("Failed to unzip: " + error)
            zip.extractall(path=dst_dir)

def download_file(url, f):
    # NOTE the stream=True parameter below
    size = -1
    while size < 0 or f.tell() < size:
        headers = { 'Range': 'bytes={}-'.format(f.tell()) }
        with get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            if size < 0:
                size = int(r.headers.get('Content-Length'))
            else:
                print()
                print('Connection reset')
            for chunk in r.iter_content(chunk_size=int(size/100)): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
                position = f.tell()
                print('\r', int(position/size*100), '%', end='', flush=True)
    print('')
