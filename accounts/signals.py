from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from accounts.models import Notification
from courses.models import Course
from payment.models import Payment

@receiver(post_save, sender=Course)
def course_added_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        users = course.enrolled_students.all()
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"{course.title}"
            )


@receiver(post_delete, sender=Course)
def course_deleted_notification(sender, instance, **kwargs):
    course = instance.course
    users = course.enrolled_students.all()
    for user in users:
        Notification.objects.create(
            user=user,
            message=f"{course.title}"
        )


@receiver(post_save, sender=Payment)
def payment_success_notification(sender, instance, created, **kwargs):
    if created and instance.status == 'success':
        user = instance.user
        Notification.objects.create(
            user=user,
            message=f"Your payment of {instance.amount} was successful."
        )