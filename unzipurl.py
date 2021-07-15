#!/usr/bin/python3

from tempfile import TemporaryFile
from zipfile import ZipFile, ZipInfo
from sys import argv
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
    """ Download and unzip a ZIP file from an URL. """
    with TemporaryFile() as temp_file:
        download_file(url, temp_file)
        temp_file.flush()
        with ZipFileWithPermissions(temp_file) as zip:
            error = zip.testzip()
            if error:
                raise ValueError("Failed to unzip {0}: {1}".format(url, error))
            zip.extractall(path=dst_dir)


def download_file(url, file):
    """ Download an URL to a file object. Recover if download is not complete when connection is reset. """
    size = -1
    while size < 0 or file.tell() < size:
        headers = { 'Range': 'bytes={}-'.format(file.tell()) }
        with get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            if size < 0:
                size = int(r.headers.get('Content-Length'))
            else:
                print()
                print('Connection reset')
            for chunk in r.iter_content(chunk_size=int(size / 100)):
                file.write(chunk)
                print('\r', int(file.tell() / size * 100), '%', end='', flush=True)
    print('')


if __name__ == "__main__":
    unzip_url(url=argv[1], dst_dir=argv[2])
