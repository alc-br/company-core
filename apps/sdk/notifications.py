class NotificationSDK:
    @staticmethod
    def send(channel, recipient, template_code, context=None):
        from apps.notifications.services import NotificationService
        return NotificationService.send_notification(channel, recipient, template_code, context)
