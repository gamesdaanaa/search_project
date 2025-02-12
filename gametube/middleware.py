
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
import re
from django.http import HttpResponseForbidden
from django.conf import settings
import logging

class WAFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('gametube.security')
        
        # WAFルール
        self.rules = {
            'sql_injection': r'(\b(select|union|insert|update|delete|drop)\b.*\b(from|into|table)\b)|(-{2})|(/\*)|(\b(or|and)\b.*\b(true|false|1|0)\b)',
            'xss': r'(<script|javascript:|vbscript:|expression\(|\b(on\w+)=)',
            'path_traversal': r'(\.\./|\.\.\\)',
            'command_injection': r'(;\s*\w+\s*[\(\|]|\|\s*\w+)',
        }

    def __call__(self, request):
        if self.is_attack(request):
            self.logger.warning(f'WAF blocked request from {request.META.get("REMOTE_ADDR")}')
            return HttpResponseForbidden('不正なリクエストを検出しました')
        return self.get_response(request)

    def is_attack(self, request):
        # リクエストデータの検査
        data = {
            'path': request.path,
            'query': request.META.get('QUERY_STRING', ''),
            'body': request.body.decode('utf-8', errors='ignore'),
            'headers': str(request.headers),
        }

        for check_type, pattern in self.rules.items():
            for value in data.values():
                if re.search(pattern, value, re.I):
                    self.logger.warning(f'Detected {check_type} attack attempt')
                    return True
        return False
