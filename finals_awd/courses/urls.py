from django.urls import path
from .views import create_course, course_list, enroll_in_course, upload_material, course_detail, browse_courses,drop_course, suspend_student, submit_assignment
from . import views
from .api import course_participant


urlpatterns = [
    path('create/', create_course, name='create_course'),

    path('', course_list, name='course_list'),
    path('enroll/<int:course_id>/', enroll_in_course, name='enroll_course'),

    path('upload/<int:course_id>/', upload_material, name = 'upload_material'),

    path('detail/<int:course_id>/', course_detail, name='course_detail'),

    path('browse/', browse_courses, name='browse_courses'),

    path('drop/<int:course_id>/',drop_course,name='drop_course'),

    #Suspend Students(Teachers)
    path('suspend/<int:course_id>/<int:student_id>/', suspend_student, name='suspend_student'),

    #Upload assignments(students)
    path('submit/<int:course_id>/', submit_assignment, name='submit_assignment'),

    #Search
    path('search/', views.search_view, name='search'),

    #API for fetching participants in course
    path('api/<int:course_id>/participants/', course_participant, name='course_participants'),


]   