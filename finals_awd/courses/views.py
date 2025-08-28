from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CourseForm, CourseMaterialForm, CourseReviewForm, SubmissionForm
from .models import Course, CourseReview

from .models import Enrollment,AssignmentSubmission

from dashboard.models import Notification
from accounts.models import CustomUser

#For search 
from django.db.models import Q
from accounts.models import CustomUser

# Create your views here.

@login_required
def create_course(request):
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    if request.method =='POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit= False)
            course.teacher = request.user
            course.save()
            return redirect('dashboard')
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form':form})


@login_required
def course_list(request):
    courses = Course.objects.all()
    enrolled_ids = Enrollment.objects.filter(student= request.user).values_list('course_id', flat=True)

    return render(request, 'courses/course_list.html', {'courses': courses,
                                                        'enrolled_ids' : enrolled_ids})

@login_required
def enroll_in_course(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.user.is_student:
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)

        if created:
            # Only notify if this is a new enrolment (not a duplicate)
            Notification.objects.create(
                recipient=course.teacher,
                course=course,
                message=f"{request.user.username} has enrolled in your course: {course.title}.",
                notification_type='enrolment'
            )

    return redirect('course_detail', course_id=course.id)

@login_required
def upload_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.teacher:
        return redirect('dashboard')
    
    if request.method =='POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            students = CustomUser.objects.filter(enrollments__course = course,
                                                 is_student = True).distinct()
            for student in students:
                Notification.objects.create(
                    recipient = student,
                    course = course,
                    message = f"New file \"{material.title}\" uploaded to {course.title}",
                    notification_type='material_upload'
                )

            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
    else:
        form = CourseMaterialForm()
        
    return render(request, 'courses/upload_material.html', {'form':form, 'course': course})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    materials = course.materials.all()
    students = course.enrollments.all()
    teacher = course.teacher



    #check if student is enrolled
    enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()

    is_enrolled_user = request.user == course.teacher or enrolled

    #Load existing review if it exists
    existing_review = CourseReview.objects.filter(course=course,student = request.user).first()
    form = CourseReviewForm(request.POST or None, instance=existing_review) if enrolled else None

    


    #Display student's submission
    submissions = None
    if request.user.is_student:
        submissions = AssignmentSubmission.objects.filter(
            course=course, student=request.user
        ).order_by('-submitted_at')
   
    

    elif request.user.is_teacher and course.teacher == request.user:
        submissions = AssignmentSubmission.objects.filter(
            course=course
        ).select_related('student').order_by('-submitted_at')

    # Fallback in case of unexpected roles
    if submissions is None:
        submissions = []

    if request.method =='POST' and form:
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.student = request.user
            review.save()
            return redirect('course_detail', course_id = course.id)
        
    #Load all reviews
    reviews = course.reviews.select_related('student').order_by('-created_at')

    return render(request,'courses/course_detail.html',{
        'course': course,
        'materials': materials,
        'students': students,
        'teacher': teacher,
        'enrolled': enrolled,
        'is_enrolled_user': is_enrolled_user,
        'form':form,
        'reviews':reviews,
        'submissions':submissions
    })

@login_required
def browse_courses(request):
    courses = Course.objects.all()
    user_courses = Course.objects.filter(teacher=request.user) if request.user.is_teacher else []

    return render(request,'courses/browse_course.html',{
        'courses':courses,
        'user_courses':user_courses,
    })

@login_required
def drop_course(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    if request.user.is_student:
        Enrollment.objects.filter(student= request.user,course_id=course_id).delete()

        #Notify course teacher
        Notification.objects.create(
            recipient = course.teacher,
            course=course,
            message = f"{request.user.username} has dropped your course: {course.title}"
        )
   
    return redirect('course_list')

@login_required
def suspend_student(request,course_id, student_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user == course.teacher and request.method =="POST":
        Enrollment.objects.filter(course=course, student_id = student_id).delete()


        #Notify student
        student = CustomUser.objects.get(id=student_id)
        Notification.objects.create(
            recipient= student,
            course = course,
            message = f"You have been suspended from {course.title}"
        )

    return redirect('course_detail', course_id=course.id)

@login_required
def submit_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    
    
    if request.method =='POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.course = course
            submission.student = request.user
            submission.save()

            Notification.objects.create(
                recipient = course.teacher,
                course = course,
                message = f"{request.user.username} submitted an assignment for {course.title}.",
                notification_type = 'assignment_submission'
            )
            

            return redirect('course_detail', course_id = course.id)
        
    else:
        form = SubmissionForm()
    
    return render(request, 'courses/submit_assignment.html',{
        'form' : form,
        'course': course
    })


# #Search bar
# @login_required
# def search_view(request):
#     query = request.GET.get('q','').strip()
#     users = CustomUser.objects.filter(
#         Q(username__icontains=query)|
#         Q(first_name__icontains=query) |
#         Q(last_name__icontains=query)
#     )

#     courses = Course.objects.filter(
#         Q(title__icontains = query)|
#         Q(description__icontains=query)
#     )

#     return render(request,'courses/search_results.html',{
#         'query':query,
#         'users':users,
#         'courses':courses
#     })

# Search bar
@login_required
def search_view(request):
    from django.db.models import Q
    from accounts.models import CustomUser
    from courses.models import Course

    raw_q = request.GET.get("q", "") or ""
    q = " ".join(raw_q.split())  # normalize whitespace

    users, courses = [], []
    if q:
        terms = [t for t in q.split(" ") if t]

        # Users: AND across tokens over username/first/last
        uq = Q()
        for t in terms:
            uq &= (Q(username__icontains=t) |
                   Q(first_name__icontains=t) |
                   Q(last_name__icontains=t))
        users = (
            CustomUser.objects.filter(uq)
            .only("id", "username", "first_name", "last_name", "is_teacher", "is_student")
            .order_by("username")[:50]
        )

        # Courses: AND across tokens over title/description
        cq = Q()
        for t in terms:
            cq &= (Q(title__icontains=t) | Q(description__icontains=t))
        courses = (
            Course.objects.filter(cq)
            .select_related("teacher")
            .only("id", "title", "description", "teacher__username")
            .order_by("title")[:50]
        )

    return render(
        request,
        "courses/search_results.html",
        {"query": q, "users": users, "courses": courses},
    )
