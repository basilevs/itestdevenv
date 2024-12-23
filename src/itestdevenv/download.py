from requests import get
from requests.exceptions import ChunkedEncodingError, ConnectionError
from progress.bar import Bar
from sys import argv

def download_file(url, file):
    """ Download an URL to a file object. Recover if download is not complete when connection is reset. """
    size = -1
    title_length = 40 
    title = url if len(url) < title_length else '...'+url[-title_length:] 
    progress = Bar(title, suffix = '%(eta_td)s')
    while size < 0 or file.tell() < size:
        headers = { 'Range': 'bytes={}-'.format(file.tell()) }
        with get(url, stream=True, headers=headers, timeout=30) as r:
            if r.status_code == 404:
                raise KeyError(url + ' is not found')
            r.raise_for_status()
            if size < 0:
                size = int(r.headers.get('Content-Length'))
                progress.max = size
            else:
                print()
                print('Connection reset')
            try:
                for chunk in r.iter_content(chunk_size=int(size / 500)):
                    file.write(chunk)
                    if progress:
                        progress.goto(file.tell())
            except ChunkedEncodingError:
                print()
                print('Connection reset')                
            except ConnectionError:
                print()
                print('Read timeout')
    if progress:
        progress.finish()
        
if __name__ == "__main__":
        with open(argv[2], 'wb') as f:
            download_file(url=argv[1], file=f)
