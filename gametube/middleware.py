
import logging
import json
from django.conf import settings

security_logger = logging.getLogger('gametube.security')

class SecurityMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # リクエストの監視
        if self.is_suspicious_request(request):
            security_logger.warning(
                'Suspicious request detected',
                extra={
                    'ip': request.META.get('REMOTE_ADDR'),
                    'path': request.path,
                    'method': request.method,
                    'user': request.user.username if request.user.is_authenticated else 'anonymous'
                }
            )

        response = self.get_response(request)
        return response

    def is_suspicious_request(self, request):
        suspicious_patterns = [
            'union select',
            'exec(',
            'eval(',
            '<script',
            'document.cookie'
        ]
        
        request_data = str(request.GET) + str(request.POST)
        return any(pattern in request_data.lower() for pattern in suspicious_patterns)
