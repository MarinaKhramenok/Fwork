import threading


class UnitOfWork:

    current = threading.local()

    def __init__(self):
        self.new_obj = []
        self.dirty_obj = []
        self.removed_obj = []

    def set_mapper_reg(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def reg_new(self, obj):
        self.new_obj.append(obj)

    def reg_dirty(self, obj):
        self.dirty_obj.append(obj)

    def reg_removed(self, obj):
        self.removed_obj.append(obj)

    def commit(self):
        self.insert_new()
        self.upd_dirty()
        self.del_removed()

    def insert_new(self):
        for obj in self.new_obj:
            self.MapperRegistry.get_mapper(obj).insert(obj)

    def upd_dirty(self):
        for obj in self.dirty_obj:
            self.MapperRegistry.get_mapper(obj).update(obj)

    def del_removed(self):
        for obj in self.removed_obj:
            self.MapperRegistry.get_mapper(obj).delete(obj)

    @staticmethod
    def new_current():
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:

    def mark_new(self):
        UnitOfWork.get_current().reg_new(self)

    def mark_dirty(self):
        UnitOfWork.get_current().reg_dirty(self)

    def mark_removed(self):
        UnitOfWork.get_current().reg_removed(self)
