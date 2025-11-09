from .management_users import MANAGER_USERNAMES

def manager_list(request):
    """
    Inyecta la lista de usernames de managers en el contexto de todos los templates.
    """
    return {
        'MANAGER_USERNAMES': MANAGER_USERNAMES
    }