from django.http import JsonResponse


class ApiException(Exception):
    def __init__(self, *errors, **kwargs):
        if kwargs != {}:
            if errors:
                errors = {None: errors, **kwargs}
            else:
                errors = kwargs
        super().__init__(str(errors))
        self.errors = errors


def api_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            if res is None:
                res = {}
            elif type(res) is not dict:
                res = {'data': res}
            res.setdefault('success', True)
            return JsonResponse(res)
        except ApiException as e:
            return JsonResponse({
                'success': False,
                'errors': e.errors
            })
    return wrapper


def api_login_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise ApiException('User is not authenticaed')
        return func(request, *args, **kwargs)
    return wrapper
