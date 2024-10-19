from .models import Activity

def log_activity(user, action, level=Activity.Level.INFO, log=""):
    Activity.objects.create(user=user, level=level, action=action, log=log)
    