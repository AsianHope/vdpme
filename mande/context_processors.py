#generates side menu based on user permissions
from mande.permissions import perms_required
from mande.urls import activity_map
def menu(request):
    user_perms = request.user.get_all_permissions()
    user_menu = []

    #loop through activity map and compare user permissions with required permissions
    for heading in activity_map:
        user_activities = []
        #for every activity listed in every heading
        for activity in heading['items']:
            check_perms = perms_required[activity['name']]
            display_activity = True
            #check to see if the user has permissions to see the item
            for perm in check_perms:
                if perm not in user_perms:
                    display_activity = False
            #if they *do* have permisisons, add it to the list of activities the user will see
            if display_activity:
                user_activities.append(activity)
        if len(user_activities):
            #rebuild activity_map for user based on their priveleges
            user_menu.append({
                'display': heading['display'],
                'icon': heading['icon'],
                'items': user_activities
            })

    return {'menu':user_menu }
