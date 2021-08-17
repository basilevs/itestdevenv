#!/usr/bin/python3

from tempfile import TemporaryFile
from zipfile import ZipFile, ZipInfo
from sys import argv
from os import chmod
from .download import download_file


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
        with ZipFileWithPermissions(temp_file) as zip_file:
            error = zip_file.testzip()
            if error:
                raise ValueError("Failed to unzip {0}: {1}".format(url, error))
            zip_file.extractall(path=dst_dir)

if __name__ == "__main__":
    unzip_url(url=argv[1], dst_dir=argv[2])
