

class TypeMapper:

    def __init__(self, table, coords, group, name, types):
        self.table = table
        self.coords = coords
        self.group = group
        self.name = name
        self.visited_group = set()
        self.forward_visited_group = set()
        self.types = types

    def merge_group(self, type_mapper):
        self.group.update(type_mapper.group)
        self.types.update(type_mapper.types)
        type_mapper.group.update(self.group)
        type_mapper.types.update(self.types)
