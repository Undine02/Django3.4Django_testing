import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_single_course(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.get('/api/v1/courses/1/')

    assert response.status_code == 200
    assert response.data['name'] == courses[0].name


@pytest.mark.django_db
def test_get_list_courses(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    for i, course in enumerate(courses):
        assert course.name == response.data[i]['name']


@pytest.mark.django_db
def test_get_filter_id_course(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.get(f'/api/v1/courses/?id={courses[1].pk}')

    assert response.status_code == 200
    assert response.data[0]['name'] == courses[1].name


@pytest.mark.django_db
def test_get_filter_name_course(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.get(f'/api/v1/courses/?name={courses[1].name}')

    assert response.status_code == 200
    assert response.data[0]['name'] == courses[1].name


@pytest.mark.django_db
def test_post_course(client, course_factory):
    response = client.post('/api/v1/courses/', data={'id': 1, 'name': 'test_name'}, format='json')

    assert response.status_code == 201
    assert response.data['name'] == 'test_name'


@pytest.mark.django_db
def test_patch_course(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.patch(f'/api/v1/courses/{courses[0].pk}/', data={'name': 'test_name'}, format='json')

    assert response.status_code == 200
    assert response.data['name'] == 'test_name'


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.delete(f'/api/v1/courses/{courses[0].pk}/')

    assert response.status_code == 204
    assert response.data is None


data = [
    (1, {"name": "test_name", "students": [1]}, 201),
    (1, {"name": "test_name", "students": [1, 2]}, 400),
]


@pytest.mark.parametrize('max_,data_,result', data)
@pytest.mark.django_db
def test_count_students_in_curse(client, settings, student_factory, max_, data_, result):
    settings.MAX_STUDENTS_PER_COURSE = max_

    students = student_factory(_quantity=2)

    response = client.post(
        path='/api/v1/courses/',
        data=data_,
        format='json'
    )

    assert response.status_code == result