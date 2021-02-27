import copy


class PrototypeMixin:

    def clone(self):
        return copy.deepcopy(self)
