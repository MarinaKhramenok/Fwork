from february_framework import Application, render
from februaryorm import UnitOfWork
from mappers import MapperRegistry
from models import TrainingSite, BaseSerializer, NotifierSms, NotifierEmail
from logging import Logger, debug
from february_framework.februarycbv import ListView, CreateView


site = TrainingSite()
logger = Logger('main')
email_notifier = NotifierEmail()
sms_notifier = NotifierSms()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_reg(MapperRegistry)

def main(request):
    logger.log('Список курсов')
    return '200 OK', render('course_list.html', objects_list=site.courses)


@debug
def create_course(request):
    if request['method'] == 'POST':
        data = request['data']
        name = data['name']
        category_id = data.get('category_id')
        print(category_id)
        category = None
        if category_id:
            category = site.find_category_by_id(int(category_id))
            course = site.create_course('record', name, category)
            course.observers.append(email_notifier)
            course.observers.append(sms_notifier)
            site.courses.append(course)
        categories = site.categories
        return '200 OK', render('create_course.html', categories=categories)
    else:
        categories = site.categories
        return '200 OK', render('create_course.html', categories=categories)


class CategoryListView(ListView):
    queryset = site.categories
    template_name = 'category_list.html'


class CategoryCreateView(CreateView):
    template_name = 'create_category.html'

    def get_cont_data(self):
        context = super().get_cont_data()
        context['categories'] = site.categories
        return context

    def create_obj(self, data: dict):
        name = data['name']
        category_id = data.get('category_id')

        category = None
        if category_id:
            category = site.find_category_by_id(int(category_id))

        new_category = site.create_category(name, category)
        site.categories.append(new_category)


def contact(request):
    if request['method'] == 'POST':
        data = request['data']
        title = data['title']
        text = data['text']
        email = data['email']
        print(f'Сообщение от {email} с темой {title} и текстом {text}')
        return '200 OK', render('contact.html')
    else:
        return '200 OK', render('contact.html')


class StudentListView(ListView):
    queryset = site.students
    template_name = 'student_list.html'


class StudentCreateView(CreateView):
    template_name = 'create_student.html'

    def create_obj(self, data: dict):
        name = data['name']
        new_obj = site.create_user('student', name)
        site.students.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()

class AddStudentCreateView(CreateView):
    template_name = 'add_student.html'

    def get_cont_data(self):
        context = super().get_cont_data()
        context['courses'] = site.courses
        context['students'] = site.students
        return context

    def create_obj(self, data: dict):
        course_name = data['course_name']
        course = site.get_course(course_name)
        student_name = data['student_name']
        student = site.get_student(student_name)
        course.add_student(student)


routes = {
    '/': main,
    '/create-course/': create_course,
    '/create-category/': CategoryCreateView(),
    '/category-list/': CategoryListView(),
    '/student-list/': StudentListView(),
    '/create-student/': StudentCreateView(),
    '/add-student/': AddStudentCreateView(),
    '/contact/': contact
}


def secret_front(request):
    #FC
    request['secret_key'] = 'something'


front = [
    secret_front
]

application = Application(routes, front)


@application.new_route('/copy-course/')
def copy_course(request):
    request_params = request['request_params']
    name = request_params['name']
    old_course = site.get_course(name)
    if old_course:
        new_name = f'copy_{name}'
        new_course = old_course.clone()
        new_course.name = new_name
        site.courses.append(new_course)

    return '200 OK', render('course_list.html', objects_list=site.courses)


@application.new_route('/category-list/')
def course_api(request):
    return '200 OK', BaseSerializer(site.courses).save()





# Запуск:
# uwsgi --http-socket :8000 --plugin python3 --wsgi-file main.py
