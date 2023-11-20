def read_map(filename):
    with open(filename, 'r') as file:
        map_string = file.read()
    map_list = [line.split(', ') for line in map_string.splitlines()]
    width = len(map_list[0]) 
    height = len(map_list)
    return map_list, width, height