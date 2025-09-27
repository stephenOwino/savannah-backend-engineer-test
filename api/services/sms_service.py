import logging

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import africastalking
except ImportError:
    africastalking = None
    logger.debug("Africa's Talking SDK not available; SMS will be simulated.")


class SMSService:
    def __init__(self):
        self.username = getattr(settings, "AFRICASTALKING_USERNAME", None)
        self.api_key = getattr(settings, "AFRICASTALKING_API_KEY", None)
        self.sender_id = getattr(settings, "AFRICASTALKING_SENDER_ID", "AFRICASTALKING")
        self._sms = None

        if africastalking and self.username and self.api_key:
            try:
                # Initialize Africa's Talking
                africastalking.initialize(self.username, self.api_key)

                # Only get the SMS service
                self._sms = africastalking.SMS
                logger.info("Africa's Talking SMS service initialized successfully")

            except africastalking.Service.AfricasTalkingException as e:
                # Handle the specific WhatsApp sandbox error
                if "Sandbox is currently not available for this service" in str(e):
                    logger.warning("WhatsApp sandbox not available, but SMS should still work")
                    # Try to get SMS service anyway - it might still be available
                    try:
                        self._sms = africastalking.SMS
                        logger.info("SMS service obtained despite WhatsApp error")
                    except (
                        AttributeError,
                        africastalking.Service.AfricasTalkingException,
                    ) as sms_error:
                        logger.warning(
                            "Could not obtain SMS service: %s. Using simulation mode.",
                            sms_error,
                        )
                        self._sms = None
                else:
                    logger.error("Africa's Talking initialization failed: %s", e)
                    self._sms = None

            except Exception as e:
                logger.error("Unexpected error initializing Africa's Talking: %s", e)
                self._sms = None
        else:
            logger.warning("Africa's Talking credentials not configured properly")

    def send_sms(self, recipients, message: str):
        if isinstance(recipients, str):
            recipients = [recipients]

        # Validate phone numbers for Kenya (+254 format)
        validated_recipients = []
        for recipient in recipients:
            if not recipient.startswith("+254") and not recipient.startswith("254"):
                # Assume it's a Kenyan number starting with 0
                if recipient.startswith("0"):
                    recipient = "+254" + recipient[1:]
                else:
                    recipient = "+254" + recipient
            validated_recipients.append(recipient)

        if not self._sms:
            logger.info("--- SIMULATED SMS ---")
            logger.info("To: %s", validated_recipients)
            logger.info("Message: %s", message)
            logger.info("Sender: %s", self.sender_id)
            logger.info("---------------------")
            return {
                "status": "simulated",
                "recipients": validated_recipients,
                "message": message,
                "SMSMessageData": {
                    "Message": "Simulated SMS sent successfully",
                    "Recipients": [{"number": num, "status": "Success", "cost": "KES 0.8000"} for num in validated_recipients],
                },
            }

        try:
            # Use the sender_id if provided
            if self.sender_id:
                response = self._sms.send(message, validated_recipients, self.sender_id)
            else:
                response = self._sms.send(message, validated_recipients)

            logger.info("Africa's Talking SMS sent successfully: %s", response)
            return response

        except Exception as exc:
            logger.exception("Error sending SMS via Africa's Talking: %s", exc)
            # Fallback to simulation if real SMS fails
            logger.info("Falling back to SMS simulation due to error")
            return {
                "status": "fallback_simulation",
                "error": str(exc),
                "recipients": validated_recipients,
                "message": message,
            }
