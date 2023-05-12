with open('bundles_9.2.info', 'r') as f:
    lines = list(f.readlines())

def line_to_name(line):
    return line.split(',')[0]

names = [line_to_name(i) for i in lines]

duplicate_names = [i for i in set(names) if names.count(i) > 1]

print(*duplicate_names)
