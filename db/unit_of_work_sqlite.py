import sqlite3
import threading

connection = sqlite3.connect('patterns.sqlite')


class RecordNotFoundExc(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')


class DbCommitExc(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdExc(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDelExc(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class PersonMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def find_by_id(self, id_person):
        statement = f"SELECT IDPERSON, FIRSTNAME, LASTNAME \
                      FROM PERSON WHERE IDPERSON='{id_person}'"
        self.cursor.execute(statement)
        result = self.cursor.fetchall()
        if result:
            return Person(*result[0])
        else:
            raise RecordNotFoundExc(f'record with id={id_person} not found')

    def insert(self, person):
        statement = f"INSERT INTO PERSON (FIRSTNAME, LASTNAME) VALUES \
                      ('{person.first_name}', '{person.last_name}')"
        self.cursor.execute(statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitExc(e.args)

    def update(self, person):
        statement = f"UPDATE PERSON SET FIRSTNAME='{person.first_name}', LASTNAME='{person.last_name}' \
                      WHERE IDPERSON='{person.id_person}'"
        self.cursor.execute(statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdExc(e.args)

    def delete(self, person):
        statement = f"DELETE FROM PERSON WHERE IDPERSON='{person.id_person}'"
        self.cursor.execute(statement)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDelExc(e.args)


class MapperRegistry:
    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Person):
            return PersonMapper(connection)


class UnitOfWork:

    current = threading.local()

    def __init__(self):
        self.new_obj = []
        self.dirty_obj = []
        self.removed_obj = []

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
            MapperRegistry.get_mapper(obj).insert(obj)

    def upd_dirty(self):
        for obj in self.dirty_obj:
            MapperRegistry.get_mapper(obj).update(obj)

    def del_removed(self):
        for obj in self.removed_obj:
            MapperRegistry.get_mapper(obj).delete(obj)

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


class Person(DomainObject):
    def __init__(self, id_person, first_name, last_name):
        self.id_person = id_person
        self.last_name = last_name
        self.first_name = first_name


class Category(DomainObject):
    def __init__(self, name):
        self.name = name


class CategoryMapper:
    pass


try:
    UnitOfWork.new_current()
    person_1 = Person(None, 'Igor', 'Igorev')
    person_1.mark_new()

    person_2 = Person(None, 'Fedor', 'Fedorov')
    person_2.mark_new()

    person_mapper = PersonMapper(connection)
    exists_person_1 = person_mapper.find_by_id(1)
    exists_person_1.mark_dirty()
    print(exists_person_1.first_name)
    exists_person_1.first_name += ' Senior'
    print(exists_person_1.first_name)

    exists_person_2 = person_mapper.find_by_id(2)
    exists_person_2.mark_removed()

    print(UnitOfWork.get_current().__dict__)

    UnitOfWork.get_current().commit()
except Exception as e:
    print(e.args)
finally:
    UnitOfWork.set_current(None)

print(UnitOfWork.get_current())
