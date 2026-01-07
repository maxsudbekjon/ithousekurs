from accounts.models import Enrollment
from course_progress.models import TestResult
from courses.models import ContactUsMessage, Video
import requests
from django.conf import settings

bot_token = settings.TELEGRAM_BOT_TOKEN
chat_id = settings.TELEGRAM_CHAT_ID

def send_telegram(self, instance: ContactUsMessage):
    
    text = (
            "🆕 Yangi so'rov keldi!\n\n"
            f"👤 Ism: {instance.full_name}\n"
            f"📞 Telefon: {instance.phone_number}\n"
            f"📚 Kurs: {instance.course.name_uz or instance.course.name_en or 'Noma\'lum'}\n"
            f"💬 Xabar:\n{instance.message}\n\n"
            f"Vaqt: {instance.created_at.strftime('%d.%m.%Y %H:%M')}"
        )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(url, data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Telegramga xabar yuborishda xato yuz berdi: {e}")


def build_video_access_map(user, course):
    course_videos = list(
        Video.objects.filter(section__course=course).select_related('test').order_by('created_at', 'id')
    )
    if not user or not user.is_authenticated:
        return {video.id: video.is_preview for video in course_videos}

    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    if not is_enrolled:
        return {video.id: video.is_preview for video in course_videos}

    passed_video_ids = set(
        TestResult.objects.filter(
            user=user,
            is_passed=True,
            test__video_id__in=[video.id for video in course_videos]
        ).values_list('test__video_id', flat=True)
    )

    access_map = {}
    for index, video in enumerate(course_videos):
        if video.is_preview or index == 0:
            access_map[video.id] = True
            continue
        prev_video = course_videos[index - 1]
        if not hasattr(prev_video, "test") or prev_video.test is None:
            access_map[video.id] = True
            continue
        access_map[video.id] = prev_video.id in passed_video_ids
    return access_map
