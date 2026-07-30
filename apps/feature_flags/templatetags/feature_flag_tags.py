from django import template

register = template.Library()


@register.tag(name='if_feature_flag')
def do_if_feature_flag(parser, token):
    """Template tag to conditionally render content based on feature flag status.

    Usage::

        {% if_feature_flag "flag_code" %}
            Content shown when flag is active.
        {% else %}
            Content shown when flag is inactive.
        {% endif_feature_flag %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("'%s' tag requires exactly one argument" % bits[0])
    flag_code = bits[1].strip('"\'')
    nodelist_true = parser.parse(('else', 'endif_feature_flag'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_feature_flag',))
        parser.next_token()
    else:
        nodelist_false = template.NodeList()
    return FeatureFlagNode(flag_code, nodelist_true, nodelist_false)


class FeatureFlagNode(template.Node):
    """Node that evaluates a feature flag and renders the appropriate nodelist."""

    def __init__(self, flag_code, nodelist_true, nodelist_false):
        self.flag_code = flag_code
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        from apps.feature_flags.services import FeatureFlagService
        request = context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        organization = getattr(request, 'tenant', None) if request else None
        if FeatureFlagService.is_active(self.flag_code, user=user, organization=organization):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)
