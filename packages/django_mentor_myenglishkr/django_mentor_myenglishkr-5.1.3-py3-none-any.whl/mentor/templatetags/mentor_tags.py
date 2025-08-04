from django.template import Library, loader

register = Library()

# https://localcoder.org/django-inclusion-tag-with-configurable-template



@register.simple_tag(takes_context=True)
def contact(context):
    """
    contact 내부에서 appointment를 처리한다.
    """
    t = loader.get_template("mentor/_contact.html")
    context.update({
        'form': AppointmentForm(),
        'post_message': context.get('post_message', None),
        'naver_link': context.get('naver', None),
    })
    return t.render(context.flatten())


