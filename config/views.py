# IdleHunter main views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required(login_url="/accounts/login/")
def home(request):
    """Redirect root to the NOC dashboard."""
    return redirect("web:dashboard")
