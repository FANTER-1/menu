from django import template
from django.urls import resolve
from menu.models import MenuItem

register = template.Library()

@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_url = request.path
    current_url_name = resolve(current_url).url_name

    menu_items = MenuItem.objects.filter(menu_name=menu_name).select_related('parent')

    def build_menu(items, parent=None):
        menu_dict = {}
        for item in items:
            if item.parent == parent:
                menu_dict[item] = build_menu(items, item)
        return menu_dict

    def is_active(item, current_url, current_url_name):
        if item.url and item.url == current_url:
            return True
        if item.named_url and item.named_url == current_url_name:
            return True
        return False

    def render_menu(menu_dict, current_url, current_url_name, level=0):
        output = []
        for item, submenu in menu_dict.items():
            active = is_active(item, current_url, current_url_name)
            output.append(f'<li class="{"active" if active else ""}">')
            output.append(f'<a href="{item.get_absolute_url()}">{item.title}</a>')
            if submenu:
                output.append('<ul>')
                output.extend(render_menu(submenu, current_url, current_url_name, level + 1))
                output.append('</ul>')
            output.append('</li>')
        return output

    menu_dict = build_menu(menu_items)
    return ''.join(render_menu(menu_dict, current_url, current_url_name))

