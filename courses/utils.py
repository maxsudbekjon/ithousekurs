from courses.models import ContactUsMessage
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