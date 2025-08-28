from dashboard.models import Notification
from chat.models import ChatNotification
from itertools import chain
from operator import attrgetter

def merged_notifications(request):
    if not request.user.is_authenticated:
        return {}

    # Fetch all (read + unread) for display
    standard = Notification.objects.filter(recipient=request.user)
    private = ChatNotification.objects.filter(recipient=request.user)

       # Add tag + common timestamp field
    for s in standard:
        s.sort_time = s.created_at

    for p in private:
        p.notification_type = 'chat'
        p.sort_time = p.timestamp

    # Merge and sort using the unified 'sort_time'
    merged = sorted(
        chain(standard, private),
        key=lambda x: x.sort_time,
        reverse=True
    )
    # Count unread from both
    unread_count = (
        standard.filter(is_read=False).count() +
        private.filter(is_read=False).count()
    )

    return {
        'merged_notifications': merged[:5],  # top 5 recent from both
        'total_unread_notifications': unread_count
    }
