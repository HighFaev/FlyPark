from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


def render(request, name: str, **context):
    context.setdefault("session", request.session)
    return templates.TemplateResponse(request, name, context)
