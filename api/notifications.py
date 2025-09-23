import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

# Mocking Africa's Talking for now. In a real project, you would:
# pip install africastalking
# import africastalking


def send_order_confirmation_sms(order):
    """Sends an SMS to the customer confirming their new order."""
    customer = order.customer
    message = (
        f"Hi {customer.user.first_name}, your order #{order.id} "
        f"for KES {order.total_amount} has been placed successfully. "
        "Thank you for shopping with us!"
    )

    try:
        # --- Africa's Talking Integration would go here ---
        # username = os.getenv('AT_USERNAME', 'sandbox')
        # api_key = os.getenv('AT_API_KEY')
        # africastalking.initialize(username, api_key)
        # sms = africastalking.SMS
        # sms.send(message, [customer.phone_number])
        logger.info("--- SIMULATING SMS ---")
        logger.info(f"To: {customer.phone_number}")
        logger.info(f"Message: {message}")
        logger.info("----------------------")
        return True
    except Exception as e:
        logger.error(f"Error sending SMS for order {order.id}: {e}")
        return False


def send_new_order_admin_email(order):
    """Sends an email to the site admin about the new order."""
    if not getattr(settings, "ADMIN_EMAIL", None):
        logger.warning("ADMIN_EMAIL not configured. Skipping admin notification.")
        return False

    subject = f"New Order Received: #{order.id}"
    message = (
        f"A new order has been placed by {order.customer.user.username}.\n\n"
        f"Order ID: {order.id}\n"
        f"Customer: {order.customer.user.get_full_name()} "
        f"({order.customer.user.email})\n"
        f"Total Amount: KES {order.total_amount}\n\n"
        "Items:\n"
    )
    for item in order.orderitem_set.all():
        message += f"- {item.quantity} x {item.product.name}\n"

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@savannah.com")

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Admin notification email sent for order #{order.id}.")
        return True
    except Exception as e:
        logger.error(f"Error sending admin email for order {order.id}: {e}")
        return False
