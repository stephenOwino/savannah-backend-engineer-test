import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .services.sms_service import SMSService

logger = logging.getLogger(__name__)


def send_order_confirmation_sms(order):
    """Send SMS confirmation to customer after order placement"""
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
    """
    Send detailed email notification to admin when new order is placed.
    Supports both HTML and plain text formats.
    """
    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if not admin_email:
        logger.error("ADMIN_EMAIL not configured; cannot send admin email.")
        return False

    customer = order.customer
    subject = f"🛒 New Order #{order.id} - {customer.user.get_full_name() or customer.user.username}"

    # Prepare order items with details
    items_data = []
    for item in order.items.all():
        items_data.append(
            {
                "product_name": item.product.name,
                "category": item.product.category.name,
                "quantity": item.quantity,
                "price": item.product.price,
                "subtotal": item.subtotal,
            }
        )

    # Context for email template
    context = {
        "order_id": order.id,
        "order_date": order.created_at,
        "customer_name": customer.user.get_full_name() or customer.user.username,
        "customer_email": customer.user.email,
        "customer_phone": customer.phone_number,
        "customer_address": customer.address or "Not provided",
        "items": items_data,
        "total_amount": order.total_amount,
        "item_count": order.items.count(),
    }

    # Try to use HTML template if available
    try:
        html_content = render_to_string("emails/new_order_admin.html", context)
        text_content = strip_tags(html_content)  # Fallback plain text

        # Create email with both HTML and plain text
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[admin_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info("Admin HTML email sent for order %s", order.id)
        return True

    except Exception as e:
        # Fallback to plain text email
        logger.warning("HTML email failed, sending plain text: %s", e)
        return send_plain_text_admin_email(order, admin_email, subject, context)


def send_plain_text_admin_email(order, admin_email, subject, context):
    """Fallback function to send plain text email if HTML fails"""
    lines = [
        "=" * 50,
        f"NEW ORDER NOTIFICATION - #{context['order_id']}",
        "=" * 50,
        "",
        "ORDER DETAILS:",
        f"  Order ID: {context['order_id']}",
        f"  Date: {context['order_date'].strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "CUSTOMER INFORMATION:",
        f"  Name: {context['customer_name']}",
        f"  Email: {context['customer_email']}",
        f"  Phone: {context['customer_phone']}",
        f"  Address: {context['customer_address']}",
        "",
        "ORDERED ITEMS:",
        "-" * 50,
    ]

    for item in context["items"]:
        lines.append(f"  • {item['product_name']} " f"(Category: {item['category']})")
        lines.append(f"    Qty: {item['quantity']} × " f"KES {item['price']} = " f"KES {item['subtotal']}")
        lines.append("")

    lines.extend(
        [
            "-" * 50,
            f"TOTAL ITEMS: {context['item_count']}",
            f"TOTAL AMOUNT: KES {context['total_amount']}",
            "",
            "=" * 50,
            "This is an automated notification from Savannah Informatics.",
            "Please process this order at your earliest convenience.",
            "=" * 50,
        ]
    )

    body = "\n".join(lines)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[admin_email],
            fail_silently=False,
        )
        logger.info("Admin plain text email sent for order %s", order.id)
        return True
    except Exception as exc:
        logger.exception("Failed to send admin email for order %s: %s", order.id, exc)
        return False
