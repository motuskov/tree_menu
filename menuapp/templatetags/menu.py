from django import template
from django.urls import reverse
from django.core.exceptions import ValidationError

from ..models import MenuItem
from ..validators import validate_path

register = template.Library()

def make_tree(flat_tree, parent=None):
    '''
    Converts list of sorted items to tree structure. Use "childs" attribute to 
    store children of an item.

    Parameters:
        flat_tree: sorted list of item objects. Each object must contain "id" 
        and "parent_id" attribute. List must be sorted in display maner.
        parent: for internal use, leave empty.
    Return:
        Top level element of created tree structure.
    '''
    while flat_tree:
        # Getting the next item, initialization children list and adding it in 
        # parent list of children
        item = flat_tree.pop()
        item.childs = []
        if parent:
            parent.childs.append(item)
        # Diving deeper if the next item is child of the current one
        if flat_tree and flat_tree[-1].parent_id == item.id:
            make_tree(flat_tree, item)
        # Going up if the next item isn't a child of parent
        if not flat_tree or not parent or flat_tree[-1].parent_id != parent.id:
            return item

@register.inclusion_tag('tags/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    '''
    Template tag function for drawing a menu on web pages.
    '''
    # Getting the current path and the current path name
    current_path = context['request'].path_info
    current_path_name = context['request'].resolver_match.url_name
    # Requesting all items of given menu name
    menu_items = list(MenuItem.objects.raw(
        'WITH RECURSIVE menu_item_tree AS ( '
            'SELECT id, '
                'name, '
                'path, '
                'parent_id, '
                'CAST(id AS TEXT) AS item_order '
            'FROM menuapp_menuitem '
            'WHERE parent_id IS NULL '
                f'AND name = "{menu_name}" '
            'UNION ALL '
                'SELECT parent_item.id, '
                    'parent_item.name, '
                    'parent_item.path, '
                    'parent_item.parent_id, '
                    'CAST('
                        'item_order '
                        '|| "_" '
                        '|| CAST(parent_item.id AS TEXT) AS TEXT'
                    ') AS item_order '
                'FROM menuapp_menuitem parent_item '
                'JOIN menu_item_tree mit '
                'ON mit.id = parent_item.parent_id '
        ') '
        'SELECT id, '
            'name, '
            'path, '
            'parent_id, '
            'item_order, '
            f'(path == "{current_path}" OR path == "{current_path_name}") AS current '
        'FROM menu_item_tree '
        'ORDER BY item_order DESC;'
    ))
    # Getting current item order
    try:
        current_item_order = list(filter(
            lambda menu_item: menu_item.current,
            menu_items
        ))[0].item_order
    except IndexError:
        current_item_order = ''
    # For each item...
    for menu_item in menu_items:
        # Setting whether it should be expaned or not
        menu_item.open = current_item_order.startswith(
            menu_item.item_order
        )
        # Checking path and converting the named url to an absolute
        try:
            validate_path(menu_item.path)
        except ValidationError:
            menu_item.path = ''
        if menu_item.path and not menu_item.path.startswith('/'):
            menu_item.path = reverse(menu_item.path)
    # Converting the items list to a tree structure
    menu = make_tree(menu_items)

    return {'menu': menu}
