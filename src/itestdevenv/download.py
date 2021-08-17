from requests import get
from progress.bar import Bar
from sys import argv

def download_file(url, file):
    """ Download an URL to a file object. Recover if download is not complete when connection is reset. """
    size = -1
    title = url if len(url) < 10 else url[-10:] 
    progress = Bar(title, suffix = '%(eta_td)s')
    while size < 0 or file.tell() < size:
        headers = { 'Range': 'bytes={}-'.format(file.tell()) }
        with get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            if size < 0:
                size = int(r.headers.get('Content-Length'))
                progress.max = size
            else:
                print()
                print('Connection reset')
            for chunk in r.iter_content(chunk_size=int(size / 500)):
                file.write(chunk)
                if progress:
                    progress.goto(file.tell())
    if progress:
        progress.finish()
        
if __name__ == "__main__":
        with open(argv[2], 'wb') as f:
            download_file(url=argv[1], file=f)
