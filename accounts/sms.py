import logging
import os

import requests
from requests import RequestException
from django.core.cache import cache

ESKIZ_BASE_URL = "https://notify.eskiz.uz/api"
ESKIZ_TOKEN_CACHE_KEY = "eskiz:token"
ESKIZ_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 25

logger = logging.getLogger(__name__)


class SmsSendError(RuntimeError):
    pass


def _get_eskiz_token():
    token = cache.get(ESKIZ_TOKEN_CACHE_KEY)
    if token:
        return token

    email = os.getenv("ESKIZ_EMAIL")
    secret = os.getenv("ESKIZ_SECRET")
    if not email or not secret:
        raise SmsSendError("Eskiz credentials are not configured")

    try:
        response = requests.post(
            f"{ESKIZ_BASE_URL}/auth/login",
            data={"email": email, "password": secret},
            timeout=10,
        )
    except RequestException as exc:
        logger.exception("Eskiz auth request failed")
        raise SmsSendError("Eskiz auth failed") from exc
    if not response.ok:
        logger.error("Eskiz auth failed: %s", response.text)
        raise SmsSendError("Eskiz auth failed")

    try:
        token = response.json().get("data", {}).get("token")
    except ValueError as exc:
        logger.exception("Eskiz auth response invalid JSON")
        raise SmsSendError("Eskiz auth failed") from exc
    if not token:
        logger.error("Eskiz auth response missing token: %s", response.text)
        raise SmsSendError("Eskiz token missing")

    cache.set(ESKIZ_TOKEN_CACHE_KEY, token, timeout=ESKIZ_TOKEN_TTL_SECONDS)
    return token


def _format_message(code):
    template = os.getenv("ESKIZ_TEMPLATE", "Tasdiqlash kodi: {code}")
    try:
        return template.format(code=code)
    except (KeyError, IndexError, ValueError) as exc:
        raise SmsSendError("Invalid ESKIZ_TEMPLATE format") from exc


def send_verification_sms(phone_number, code):
    message = _format_message(code)
    sender = os.getenv("ESKIZ_FROM")
    payload = {
        "mobile_phone": phone_number.replace("+", ""),
        "message": message,
    }
    if sender:
        payload["from"] = sender

    token = _get_eskiz_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{ESKIZ_BASE_URL}/message/sms/send",
            headers=headers,
            data=payload,
            timeout=10,
        )
    except RequestException as exc:
        logger.exception("Eskiz sms request failed")
        raise SmsSendError("SMS send failed") from exc
    if response.status_code == 401:
        cache.delete(ESKIZ_TOKEN_CACHE_KEY)
        token = _get_eskiz_token()
        headers["Authorization"] = f"Bearer {token}"
        try:
            response = requests.post(
                f"{ESKIZ_BASE_URL}/message/sms/send",
                headers=headers,
                data=payload,
                timeout=10,
            )
        except RequestException as exc:
            logger.exception("Eskiz sms retry failed")
            raise SmsSendError("SMS send failed") from exc

    if not response.ok:
        logger.error("Eskiz sms send failed: %s", response.text)
        raise SmsSendError("SMS send failed")

    try:
        return response.json()
    except ValueError as exc:
        logger.exception("Eskiz sms response invalid JSON")
        raise SmsSendError("SMS send failed") from exc
