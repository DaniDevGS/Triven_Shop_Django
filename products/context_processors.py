from .management_users import MANAGER_USERNAMES

def manager_list(request):
    """
    Inyecta la lista de usernames de managers en el contexto de todos los templates.
    """
    return {
        'MANAGER_USERNAMES': MANAGER_USERNAMES
    }

def cart_count(request):
    """
    Calcula el número total de productos (ítems) en el carrito de la sesión
    y lo inyecta en el contexto de la plantilla.
    """
    # Obtener el diccionario del carrito de la sesión
    cart = request.session.get('cart', {})
    
    total_items = 0
    
    # Recorrer los productos en el carrito y sumar la cantidad de cada uno
    # El diccionario 'cart' tiene la forma: {'producto_id_str': {'cantidad': X, ...}}
    for item_data in cart.values():
        # Sumamos la cantidad de cada producto
        total_items += item_data.get('cantidad', 0)
        
    return {
        # Esta variable estará disponible en todos los templates
        'cart_item_count': total_items 
    }