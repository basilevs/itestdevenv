from itertools import takewhile

from jenkins import Jenkins
from os import environ, unlink, makedirs
from sys import stderr
from subprocess import run, PIPE
from base64 import b64encode
from urllib.request import urlretrieve, Request, urlopen
from zipfile import ZipFile
from os.path import abspath, join

def download_distribution(job, build):
    targetDir = join("C:\\Users\\basil\\Documents\\Xored\\itest\\installations", job, str(build))
    makedirs(targetDir, exist_ok=True)
    file, message = urlretrieve("https://artifactory-ito.spirenteng.com/artifactory/apt-jenkins-itest-builds/%s/itest/%d/iTestTeam-win32.win32.x86_64.zip" % (job, build))
    try:

        with ZipFile(file) as zip_ref:
            zip_ref.extractall(targetDir)
    finally:
        unlink(file)

download_distribution('branches', 2923)
