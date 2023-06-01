from sys import stdin

skip = False
for line in stdin.readlines():
	if line.startswith('Product:'):
		skip = 'lite' in line or 'Lite' in line
	if not skip:
		print(line, end='')