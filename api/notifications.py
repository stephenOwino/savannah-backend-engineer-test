import logging

from django.conf import settings
from django.core.mail import send_mail

from .services.sms_service import SMSService

logger = logging.getLogger(__name__)


def send_order_confirmation_sms(order):
    customer = order.customer
    message = (
        f"Hi {customer.user.first_name or customer.user.username}, "
        f"your order #{order.id} for KES {order.total_amount} has been placed. "
        "Thank you."
    )
    try:
        sms = SMSService()
        resp = sms.send_sms([customer.phone_number], message)
        logging.info("send_order_confirmation_sms result: %s", resp)
        return resp
    except Exception as e:
        logging.warning("Failed to send order SMS: %s", e)
        return {"status": "failed", "error": str(e)}


def send_new_order_admin_email(order):
    # Notify admin by email, if configured.
    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if not admin_email:
        logger.info("ADMIN_EMAIL not configured; skipping admin email.")
        return False

    subject = f"New order received: #{order.id}"
    lines = [
        f"Order ID: {order.id}",
        f"Customer: {order.customer.user.get_full_name()} ({order.customer.user.email})",
        f"Total: {order.total_amount}",
        "Items:",
    ]
    for item in order.items.all():
        lines.append(f"- {item.quantity} × {item.product.name}")

    body = "\n".join(lines)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    try:
        send_mail(subject, body, from_email, [admin_email], fail_silently=False)
        logger.info("Admin email sent for order %s", order.id)
        return True
    except Exception as exc:
        logger.exception("Failed to send admin email for order %s: %s", order.id, exc)
        return False