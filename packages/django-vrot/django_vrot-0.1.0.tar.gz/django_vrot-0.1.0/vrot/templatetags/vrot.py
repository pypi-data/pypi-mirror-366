from urllib.parse import urlencode

from django import template
from django.urls import reverse
from django.utils.encoding import escape_uri_path

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(
    context, viewname, css_class="menu-active", css_inactive_class="", strict=False
):
    """
    Renders the given CSS class if the request path matches the path of the view.
    :param context: The context where the tag was called. Used to access the request object.
    :param viewnames: The name of the view or views separated by || (include namespaces if any).
    :param css_class: The CSS class to render if the view is active.
    :param css_inactive_class: The CSS class to render if the view is not active.
    :param strict: If True, the tag will perform an exact match with the request path.
    :return:
    """
    request = context.get("request")
    if request is None:
        # Can't work without the request object.
        return css_inactive_class

    active = False
    request_path = escape_uri_path(request.path)
    path = reverse(viewname.strip())

    if strict or path == "/":
        active = request_path == path
    else:
        active = request_path.startswith(path)

    return css_class if active else css_inactive_class


@register.filter
def getitem(array, i):
    """
    Get a value from a list or dict

    Example:
        {% load vrot %}
        {{ my_dict|getitem:my_key }}
    """
    try:
        return array[i]
    except (IndexError, KeyError):
        return ""


@register.simple_tag(takes_context=True)
def query_param_replace(context, **kwargs):
    """
    Replaces one query param's value with something else, without replacing the other query parameters.
    This is helpful if you want to keep filtering parameters intact while enabling previous/next pagination
    links which should modify the `page` query parameter.

    Example:
        {% load vrot %}
        <a href="{% param_replace page=page_obj.previous_page_number %}">Previous</a>
    """
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value

    return "?" + urlencode(query, doseq=True)
