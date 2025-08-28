from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course,Enrollment
from .models import StatusUpdate
from .forms import StatusUpdateForm, CommentForm

from .models import Notification

from dashboard.models import Notification
from chat.models import ChatNotification
from accounts.models import CustomUser
from itertools import chain
from operator import attrgetter

from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def dashboard_view(request):
    user = request.user

    if user.is_teacher:
        courses = Course.objects.filter(teacher=user)
        all_courses = Course.objects.all()
    elif user.is_student:
        courses = Course.objects.filter(enrollments__student=user)
        all_courses = None
    else:
        courses = []

    # Initialize forms early
    form = StatusUpdateForm()
    comment_form = CommentForm()

    if request.method == 'POST':
        if 'status_submit' in request.POST:
            form = StatusUpdateForm(request.POST)
            if form.is_valid():
                status = form.save(commit=False)
                status.user = user
                status.save()

                participants = CustomUser.objects.filter(
                    enrollments__course__in=courses
                ).distinct()

                for participant in participants:
                    if participant != user:
                        Notification.objects.create(
                            recipient=participant,
                            message=f"{user.username} posted: \"{status.content[:50]}...\"",
                            notification_type='status_post'
                        )

                return redirect('dashboard')

        elif 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = user
                comment.status_id = request.POST.get('status_id')
                comment.save()

                if comment.status.user != user:
                    Notification.objects.create(
                        recipient=comment.status.user,
                        message=f"{user.username} commented on your status: \"{comment.content[:50]}...\"",
                        notification_type='status_comment'
                    )

                return redirect('dashboard')

    statuses = StatusUpdate.objects.all().order_by('-posted_on')[:5]


    return render(request, 'dashboard/dashboard.html', {
        'user': user,
        'courses': courses,
        'all_courses': all_courses,
        'statuses': statuses,
        'form': form,
        'comment_form': comment_form,
    })


@login_required
def load_more_statuses(request):
    offset = int(request.GET.get('offset', 0))
    limit = 5
    statuses = StatusUpdate.objects.all().order_by('-posted_on')[offset:offset + limit]
    html = render_to_string('dashboard/partials/status_list.html', {'statuses': statuses}, request=request)
    has_more = StatusUpdate.objects.count() > offset + limit
    return JsonResponse({'html': html, 'has_more': has_more})

@login_required
def view_notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})

@login_required
def all_notifications_view(request):
    notif = Notification.objects.filter(recipient=request.user)
    chat = ChatNotification.objects.filter(recipient=request.user)

    for n in notif:
        n.sort_time = n.created_at

    for c in chat:
        c.notification_type = 'chat'
        c.sort_time = c.timestamp

    merged = sorted(
        chain(notif, chat),
        key=attrgetter('sort_time'),
        reverse=True
    )

    # Mark all as read
    notif.filter(is_read=False).update(is_read=True)
    chat.filter(is_read=False).update(is_read=True)

    return render(request, 'dashboard/all_notifications.html', {
        'notifications': merged
    })