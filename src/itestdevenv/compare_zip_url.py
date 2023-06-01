from requests import head
from tempfile import TemporaryFile
from sys import argv
from .list_zip import list_zip, remove_version_from_name


from .download import download_file


def unzip_url(url):
    with TemporaryFile() as temp_file:
        download_file(url, temp_file)
        temp_file.flush()
        temp_file.seek(0)
        return list_zip(temp_file)
    



def diff_lists(a: list, b: list):
    a = set(a)
    b = set(b)
    return (set(a) - set(b), set(b) - set(a))


def compare_zip_url(url1, url2):
    # get all file names from zip
    # remove version from file names
    # compare lists
    return diff_lists(
        map(remove_version_from_name, unzip_url(url1)),
        map(remove_version_from_name, unzip_url(url2))
    )


def ensure_exists(url):
    head(url).raise_for_status()


def compare_urls(prefix1: str, prefix2: str, *suffixes: str):
    for suffix in suffixes:
        url_a = prefix1+suffix
        url_b = prefix2+suffix
        ensure_exists(url_a)
        ensure_exists(url_b)

    for suffix in suffixes:
        url_a = prefix1+suffix
        url_b = prefix2+suffix
        removed, added = compare_zip_url(url_a, url_b)
        with open(suffix+'.txt', 'w') as f:
            f.write('Comparing {} and {}\n'.format(url_a, url_b))
            f.write('Removed:\n')
            removed = list(removed)
            removed.sort()
            for name in removed:
                f.write("-" + name+'\n')
            f.write('Added:\n')
            added = list(added)
            added.sort()
            for name in added:
                f.write("+" + name+'\n')


if '__main__' == __name__:
    compare_urls(argv[1], argv[2], *argv[3:])
