from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    def wrapper():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="bE app",
            version="1.0.0",
            description="app for tut fastapi",
            routes=app.routes,
        )
        user_header = {
            "name": "user_id",
            "in": "header",
            "required": True,
            "schema": {
                "type": "integer",
                "example": "1",
            },
            "type": "integer",
        }
        paths = openapi_schema["paths"]
        for key in paths.keys():
            path = paths[key]
            if "get" in path.keys():
                path["get"]["parameters"].append(user_header)
            if "post" in path.keys():
                path["post"]["parameters"].append(user_header)

        return openapi_schema

    return wrapper
