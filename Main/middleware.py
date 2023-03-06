import jwt

def proxy_authorization():
    data={
    "current_period_started_at": 8,
    "exp": 1876398251,
    "instance_id": 2,
    "role": "HR",
    "user_email": "ahmedmulla1910@gmail.com",
    "user_id": 1,
    "user_name": "User 1",
    "workspace_id": 1,
    "workspace_name": "Cohesive"
    }

    secret="b05a04aa337feb98b3984c596522b2533b54647898c2863022a352fa8156651c5a7e0c97c0db982d284981d33c814a356953f097dd9bcce838f9e98c26aea904"

    encoded_jwt = jwt.encode(data,secret, algorithm="HS256")
    
    
    return("Bearer "+(encoded_jwt))

class ProxyAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        
        
        request.META['HTTP_AUTHORIZATION'] = proxy_authorization()
        
        response = self.get_response(request)
        
        return response

