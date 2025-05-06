def driver_profile(request):
    """
    Add driver profile to template context if user is a driver
    """
    context = {
        'is_driver': False,
        'driver': None
    }
    
    if request.user.is_authenticated:
        try:
            context['driver'] = request.user.driver
            context['is_driver'] = True
        except:
            pass
    
    return context 