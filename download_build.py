#!/usr/bin/python3

#from jenkins import Jenkins
#from os import environ
from tempfile import gettempdir
from os.path import join, exists
from pprint import pprint
from sys import argv
from unzipurl import unzip_url
from platform import system

suffix = None
if system() == 'Windows':
    suffix = 'win32.win32.x86_64.zip'
elif system() == 'Linux':
    suffix = 'linux.gtk.x86_64.zip'
    
url_template = "https://artifactory-ito.spirenteng.com/artifactory/apt-jenkins-itest-builds/{0}/{1}/{2}/iTest-" + suffix

def build_url(job, number):
    project, name = job.split("--")
    return url_template.format(name, project, number)

def download_build(job, number):
    dst_dir = join(gettempdir(), 'itest', job, str(number))
    if exists(dst_dir):
        raise ValueError(dst_dir + ' already exists')
    unzip_url(build_url(job, number), dst_dir)
    print('Unzipped to ' + dst_dir)
    
            

if __name__ == "__main__":
    download_build(job=argv[1], number=int(argv[2]))
    #download_build('itest--branches', 4189)
