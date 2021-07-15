#!/usr/bin/python3

# from jenkins import Jenkins
# from os import environ
from tempfile import gettempdir
from os.path import join, exists
from os import makedirs
from pprint import pprint
from sys import argv
from unzipurl import unzip_url
from platform import system


def build_url(job, number):
    system_to_suffix = {'Windows': 'win32.win32.x86_64', 'Linux': 'linux.gtk.x86_64', 'Darwin': 'macosx.cocoa.x86_64'}
    try:
        suffix = system_to_suffix[system()]
    except:
        raise KeyError("Unknown system " + system())    
    url_template = "https://artifactory-ito.spirenteng.com/artifactory/apt-jenkins-itest-builds/{0}/{1}/{2}/iTest-{3}.zip" 
    project, name = job.split("--")
    return url_template.format(name, project, number, suffix)


def _write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)


def configure_itest(unzip_root):
    settings_dir = join(unzip_root, 'iTest', 'configuration', '.settings')
    makedirs(settings_dir,)
    _write_file(join(settings_dir, 'com.fnfr.svt.configuration.licensing.flexlm.prefs'), """eclipse.preferences.version=1
licensePath=
licenseServers=englshost.spirenteng.com\:-1;
useLicenseFile=false
useLicenseServer=true
""")
    _write_file(join(settings_dir, 'com.fnfr.itest.platform.configuration.prefs'), """borrowUntil=1625849999999
borrowingEnabled=false
eclipse.preferences.version=1
selectedProductModules=
selectedProductType=com.fnfr.producttypes.enterprise
""")
    with open(join(unzip_root, 'iTest', 'iTest.ini'), 'a') as f:
        f.write('-agentlib:jdwp=transport=dt_socket,server=y,address=8000,suspend=n\n')


def download_build(job, number):
    dst_dir = join(gettempdir(), 'itest', job, str(number))
    if exists(dst_dir):
        raise ValueError(dst_dir + ' already exists')
    unzip_url(build_url(job, number), dst_dir)
    print('Unzipped to ' + dst_dir)
    configure_itest(dst_dir)
            

if __name__ == "__main__":
    download_build(job=argv[1], number=int(argv[2]))
    # download_build('itest--branches', 4189)
