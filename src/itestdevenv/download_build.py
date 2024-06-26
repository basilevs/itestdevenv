#!/usr/bin/python3

# from jenkins import Jenkins
# from os import environ
from tempfile import gettempdir
from os.path import join, exists
from os import makedirs
from pprint import pprint
from sys import argv
from platform import system, machine
from requests import get

from .unzipurl import unzip_url


def architecture_suffix():
    processor_to_suffix = {'x86_64': 'x86_64', 'arm': 'aarch64', 'AMD64':'x86_64', 'arm64': 'aarch64'}
    try:
        return processor_to_suffix[machine()]
    except KeyError:
        raise KeyError('Unknown processor ' + machine())

# https://artifactory-ito.spirenteng.com/artifactory/apt-jenkins-itest-builds/v9.3.0/itest/283/iTest-linux.gtk.x86_64.zip
_url_prefix_template = "https://artifactory-ito.spirenteng.com/artifactory/apt-jenkins-itest-builds/{0}/{1}"

def url_prefix(job):
    try:
        name, folder  = job.split('/')
    except ValueError:
        folder, name = job.split("--")
    return _url_prefix_template.format(name, folder)

def latest_build(url_prefix):
    version_url = url_prefix + '/latest/version.txt'
    response = get(version_url)
    response.raise_for_status()
    return int(response.text)

def build_url(prefix, number, architecture='x86_64', product='iTest'):
    system_to_suffix = {'Windows': 'win32.win32', 'Linux': 'linux.gtk', 'Darwin': 'macosx.cocoa'}
    try:
        suffix = system_to_suffix[system()]
    except:
        raise KeyError("Unknown system " + system())
    suffix = suffix + '.' + architecture
    return prefix + "/{0}/{1}-{2}.zip".format(number, product, suffix)


def _write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

tempdir = join(gettempdir(), 'itest')

def configure_itest(unzip_root):
    product_root = join(unzip_root, 'iTest')
    if not exists(product_root):
        product_root = join(unzip_root, 'iTest.app', 'Contents', 'Eclipse')
    if not exists(product_root):
        raise ValueError("Can't find product dir in " + unzip_root)
    settings_dir = join(product_root, 'configuration', '.settings')
    makedirs(settings_dir, exist_ok=True)
    _write_file(join(settings_dir, 'com.fnfr.svt.configuration.licensing.flexlm.prefs'), 
             """eclipse.preferences.version=1
                licensePath=
                licenseServers=lic\://englshost.spirenteng.com;
                useLicenseFile=false
                licensingProxyServer.host=englshost.spirenteng.com
                licensingProxyServer.port=9011
                useLicenseServer=true
             """)
    _write_file(join(settings_dir, 'com.fnfr.itest.platform.configuration.prefs'), 
     """borrowUntil=1625849999999
        borrowingEnabled=false
        eclipse.preferences.version=1
        selectedProductModules=
        selectedProductType=com.fnfr.producttypes.enterprise
     """)
    workspace_dir = join(tempdir, 'ws', '1').replace('\\', '\\\\')
    _write_file(join(settings_dir, 'org.eclipse.ui.ide.prefs'),
         f"""MAX_RECENT_WORKSPACES=10
            RECENT_WORKSPACES={workspace_dir}
            RECENT_WORKSPACES_PROTOCOL=3
            SHOW_RECENT_WORKSPACES=false
            SHOW_WORKSPACE_SELECTION_DIALOG=false
            eclipse.preferences.version=1
         """)
    with open(join(product_root, 'iTest.ini'), 'a') as f:
        f.write('-agentlib:jdwp=transport=dt_socket,server=y,address=127.0.0.1:8000,suspend=n\n')

def download_itest(job, number=None):
    dst_dir = download_build(job, number, 'iTest')
    configure_itest(dst_dir)

def download_itestrt(job, number):
    download_build(job, number, 'iTestRT')

def download_ndo(job, number):
    download_build(job, number, 'ndo')

def download_build(job, number, product):
    prefix = url_prefix(job)
    if not number:
        number = latest_build(prefix)
    dst_dir = join(tempdir, job, str(number), product)
    if exists(dst_dir):
        raise ValueError(dst_dir + ' already exists')
    
    def try_arch(architecture):
        unzip_url(build_url(prefix, number, architecture=architecture, product=product), dst_dir) 
    arch = architecture_suffix()
    try:
        try_arch(arch)
    except KeyError:
        if arch != 'x86_64':
            try_arch('x86_64')
        else:
            raise
            
    print('Unzipped to ' + dst_dir)
    return dst_dir

            
if __name__ == "__main__":
    number = None
    if len(argv) > 2:
        number=int(argv[2])
    download_itest(job=argv[1], number=number)
    # download_build('itest--branches', 4189)
