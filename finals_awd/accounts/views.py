from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, ProfilePictureForm

from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from django.contrib import messages
# Create your views here.

from accounts.models import CustomUser

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
        else:
            print("Form is invalid:", form.errors)  # Optional debug
            # Fall through to render the form with errors below
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user

    if user.is_teacher:
        courses = Course.objects.filter(teacher=user)
    elif user.is_student:
        courses = Course.objects.filter(enrollments__student = user)
    else:
        courses = []

    return render(request,'accounts/profile.html',{
        'user_profile': user,
        'related_courses': courses
    })

@login_required
def edit_profile(request):
    user = request.user
    if request.method =='POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfilePictureForm(instance=user)
    
    return render(request, 'accounts/edit_profile.html',{'form': form})


@login_required
def public_profile(request, user_id, course_id):
    user_profile = get_object_or_404(CustomUser,id=user_id )
    course = get_object_or_404(Course, id =course_id)

    #Only fetch and check course access if course_id is provided
    if course_id and course_id != 0:
        try:
            course=Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise Http404("Course does not exist")
        

        is_participant = (
            request.user == course.teacher or
            request.user.enrollments.filter(course=course).exists()
        )

        if not is_participant:
            messages.warning(request, "You must be enrolled in this course to view this profile.")
            return redirect('course_detail', course_id=course_id)
    
    #For teacher viewing- show taught courses
    if user_profile.is_teacher:
        related_courses = Course.objects.filter(teacher=user_profile)

    elif user_profile.is_student:
        related_courses = Course.objects.filter(enrollments__student = user_profile)
    else:
        related_courses = []

    return render(request, 'accounts/public_profile.html',{
        'user_profile': user_profile,
        'related_courses': related_courses,
        'course':course
    })
    
@login_required
def public_profile_simple(request, user_id):
    user_profile = get_object_or_404(CustomUser, id=user_id)

    if user_profile.is_teacher:
        related_courses = Course.objects.filter(teacher=user_profile)
    elif user_profile.is_student:
        related_courses = Course.objects.filter(enrollments__student=user_profile)
    else:
        related_courses = []

    return render(request, 'accounts/public_profile.html', {
        'user_profile': user_profile,
        'related_courses': related_courses,
        'course': None
    })
