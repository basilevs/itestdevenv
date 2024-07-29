
from pathlib import Path
from re import compile


filename_pattern = compile('([^_]+)_(.*).jar')

def read_plugin_directory(path: Path):
    for child in path.iterdir():
        match = filename_pattern.match(child.name)
        if match:
            yield match.group(1), match.group(2)

number_pattern = compile('\\d+')
def normalize_segments(segments:list):
    for segment in segments:
        match = number_pattern.search(segment)
        if match:
            if match.start() > 0:
                yield segment[:match.start()]
            yield segment[match.start():match.end()]
            if match.end() < len(segment) - 1: 
                yield from normalize_segments([segment[match.end():]])
        else:
            yield segment
        
def parse_version(version: str) -> list:
    return list(normalize_segments(version.split('.')))

def compare_lists(list1, list2, element_compare):
    list2=list(list2)
    for element1 in list1:
        element2 = list2.pop(0)
        result = element_compare(element1, element2)
        if result == 0:
            continue
        return result

def compare_segments(segment1, segment2):
    try:
        return int(segment1) - int(segment2)
    except ValueError:
        if segment1 < segment2:
            return -1
        if segment2 < segment1:
            return 1
        return 0

def collect_latest(plugin_versions: list):
    latest_plugins = {}
    for plugin, version in plugin_versions:
        current_version = latest_plugins.get(plugin, '')
        try:
            if compare_lists(parse_version(current_version), parse_version(version), compare_segments) < 0:
                latest_plugins[plugin] = version
        except TypeError:
            raise ValueError(current_version, version)
    return latest_plugins


before = collect_latest(read_plugin_directory(Path('/tmp/mirror/mirror_dependencies/itest/128/dependencies/plugins')))
after = collect_latest(read_plugin_directory(Path('/tmp/mirror/mirror_dependencies/itest/161/repository/plugins')))

print("Plug-in", "Old version", "New version", sep=',')
for plugin, version in after.items():
    old_version = before.get(plugin, None)
    if old_version != version:
        print(plugin, old_version, version, sep=',')
