import logging

from django.conf import settings
from django.core.mail import send_mail

from .services.sms_service import SMSService

logger = logging.getLogger(__name__)


def send_order_confirmation_sms(order):
    customer = order.customer
    first_item = order.items.first()
    item_summary = f"{first_item.product.name} (x{first_item.quantity})" if first_item else "items"

    message = (
        f"Hi {customer.user.first_name or customer.user.username}, "
        f"your order #{order.id} ({item_summary}...) for KES {order.total_amount} has been placed. "
        "Thank you for shopping with Savannah."
    )

    try:
        sms = SMSService()
        resp = sms.send_sms([customer.phone_number], message)
        logger.info("send_order_confirmation_sms result: %s", resp)
        return resp
    except Exception as e:
        logger.warning("Failed to send order SMS: %s", e)
        return {"status": "failed", "error": str(e)}


def send_new_order_admin_email(order):
    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if not admin_email:
        logger.error("ADMIN_EMAIL not configured; cannot send admin email.")
        return False

    customer = order.customer
    subject = f"New Order #{order.id} from {customer.user.get_full_name() or customer.user.username}"

    lines = [
        f"Order ID: {order.id}",
        f"Customer: {customer.user.get_full_name()} ({customer.user.email})",
        f"Phone: {customer.phone_number}",
        f"Total: KES {order.total_amount}",
        "",
        "Items:",
    ]

    for item in order.items.all():
        lines.append(f"- {item.quantity} × {item.product.name}")

    lines.append("\nThis is an automated notification from Savannah Informatics.")
    body = "\n".join(lines)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    try:
        send_mail(subject, body, from_email, [admin_email], fail_silently=False)
        logger.info("Admin email sent for order %s", order.id)
        return True
    except Exception as exc:
        logger.exception("Failed to send admin email for order %s: %s", order.id, exc)
        return False
