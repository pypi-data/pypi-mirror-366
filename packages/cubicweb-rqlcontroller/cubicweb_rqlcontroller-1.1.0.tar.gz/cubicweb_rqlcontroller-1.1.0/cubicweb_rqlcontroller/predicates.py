from cubicweb.predicates import ExpectedValuePredicate, Predicate


class match_all_http_headers(ExpectedValuePredicate):
    """Return non-zero score if all HTTP headers are present"""

    def __call__(self, cls, request, **kwargs):
        for value in self.expected:
            if not request.get_header(value):
                return 0

        return 1


class match_basic_auth(Predicate):
    def __call__(self, cls, request, **kwargs):
        authorization = request.get_header("Authorization")
        if not authorization:
            return 0
        try:
            method, _ = authorization.split(None, 1)
        except ValueError:
            return 0
        return int(method.lower() == "basic")
