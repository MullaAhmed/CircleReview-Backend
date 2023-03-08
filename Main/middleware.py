import jwt

def proxy_authorization():
    data={
    "current_period_started_at": 8,
    "exp": 1876398251,
    "instance_id": 2,
    "role": "HR",
    "user_email": "ahmedmulla8008@gmail.com",
    "user_id": 4,
    "user_name": "User 4",
    "workspace_id": 1,
    "workspace_name": "Cohesive"
    }

    secret="ef5c72677c299900f981d7da3d955c042931d97b58901b3cd1594ad591ede162e82d1edb9110023be82f7a856efd478969488984c87667aafdcec938cc59da61"

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

