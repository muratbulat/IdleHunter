# IdleHunter main views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# Full home page template: modern dark UI + Idle toggle (kept for reference; root now redirects to dashboard)
HOME_HTML = r"""
{% load i18n %}
<!DOCTYPE html>
<html lang="{{ request.LANGUAGE_CODE|default:'tr' }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% trans "IdleHunter" %}</title>
    <style>
        :root { --bg: #0f0f14; --surface: #1a1a24; --border: #2d2d3a; --text: #e4e4e7; --text-muted: #a1a1aa; --accent: #22c55e; --accent-dim: #16a34a; --link: #38bdf8; --link-hover: #7dd3fc; --danger: #f87171; --card-radius: 12px; }
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; margin: 0; padding: 0; background: var(--bg); color: var(--text); line-height: 1.6; min-height: 100vh; }
        header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0.75rem 1.5rem; }
        header nav { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; max-width: 72rem; margin: 0 auto; }
        header a { color: var(--link); text-decoration: none; font-weight: 500; }
        header a:hover { color: var(--link-hover); }
        header .user { color: var(--text-muted); }
        header .btn-link { background: none; border: none; color: var(--link); cursor: pointer; font: inherit; padding: 0; text-decoration: none; }
        header .btn-link:hover { color: var(--link-hover); }
        main { max-width: 72rem; margin: 0 auto; padding: 1.5rem; }
        h1 { font-size: 1.75rem; font-weight: 700; margin: 0 0 1.25rem 0; letter-spacing: -0.02em; }
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--card-radius); padding: 1.25rem; margin-bottom: 1.5rem; }
        .card h2 { font-size: 1.1rem; font-weight: 600; margin: 0 0 0.75rem 0; color: var(--text); }
        .card p { margin: 0.5rem 0; color: var(--text-muted); font-size: 0.95rem; }
        .card a { color: var(--link); }
        .card a:hover { color: var(--link-hover); }
        .stats { display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 0.75rem 0; }
        .stat { background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 8px; padding: 0.5rem 1rem; font-weight: 600; color: var(--accent); }
        .section-title { font-size: 1.05rem; font-weight: 600; margin: 1.5rem 0 0.75rem 0; }
        table { width: 100%; border-collapse: collapse; background: var(--surface); border-radius: var(--card-radius); overflow: hidden; border: 1px solid var(--border); }
        th, td { text-align: left; padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); }
        th { background: rgba(0,0,0,0.2); font-weight: 600; font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.03em; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(255,255,255,0.02); }
        .badge { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 6px; font-size: 0.8rem; font-weight: 500; }
        .badge-idle { background: rgba(248, 113, 113, 0.2); color: var(--danger); }
        .badge-active { background: rgba(34, 197, 94, 0.2); color: var(--accent); }
        .badge-missing { background: rgba(161, 161, 170, 0.3); color: var(--text-muted); }
        .btn { display: inline-block; padding: 0.4rem 0.75rem; border-radius: 8px; font-size: 0.85rem; font-weight: 500; cursor: pointer; border: none; text-decoration: none; transition: background 0.15s; }
        .btn-sm { padding: 0.3rem 0.6rem; font-size: 0.8rem; }
        .btn-idle { background: var(--danger); color: #fff; }
        .btn-idle:hover { background: #ef4444; }
        .btn-active { background: var(--accent); color: #0f0f14; }
        .btn-active:hover { background: var(--accent-dim); color: #fff; }
        form { display: inline; }
        select { background: var(--surface); color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 0.35rem 0.5rem; font-size: 0.9rem; }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/">{% trans "IdleHunter" %}</a>
            <form action="{% url 'set_language' %}" method="post">{% csrf_token %}
                <input name="next" type="hidden" value="{{ request.get_full_path }}">
                <label for="language">{% trans "Language" %}:</label>
                <select name="language" id="language" onchange="this.form.submit()">
                    {% get_current_language as CURRENT_LANG %}
                    {% get_available_languages as LANGUAGES_LIST %}
                    {% for code, name in LANGUAGES_LIST %}
                        <option value="{{ code }}" {% if code == CURRENT_LANG %}selected{% endif %}>{{ name }}</option>
                    {% endfor %}
                </select>
            </form>
            {% if user.is_authenticated %}
                <span class="user">{{ user.get_username }}</span>
                <form action="{% url 'logout' %}" method="post" style="display: inline;">{% csrf_token %}
                    <button type="submit" class="btn-link">{% trans "Log out" %}</button>
                </form>
            {% else %}
                <a href="{% url 'login' %}">{% trans "Log in" %}</a>
            {% endif %}
        </nav>
    </header>
    <main>
        <h1>{% trans "IdleHunter" %}</h1>
        <section class="card">
            <h2>{% trans "Dashboard" %}</h2>
            <p>{% trans "Idle VM detection — base setup is running." %}</p>
            <div class="stats">
                <span class="stat">{% trans "Data sources" %}: {{ data_source_count|default:0 }}</span>
                <span class="stat">{% trans "Virtual machines" %}: {{ vm_count|default:0 }}</span>
                <span class="stat">{% trans "Scan runs" %}: {{ scan_run_count|default:0 }}</span>
            </div>
            <p><a href="/admin/">{% trans "View and manage in Admin" %} →</a> <a href="/dashboard/">{% trans "Dashboard" %} →</a></p>
        </section>
        {% if recent_vms %}
        <h3 class="section-title">{% trans "Recent VMs" %}</h3>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin: 0 0 0.5rem 0;">{% trans "Status is based on resource usage: Active (in use), Idle (low/no usage), Missing (not seen in recent scans)." %}</p>
        <table>
            <thead><tr><th>{% trans "Name" %}</th><th>{% trans "Source" %}</th><th>{% trans "Last seen" %}</th><th>{% trans "Status" %}</th><th>{% trans "Score" %}</th></tr></thead>
            <tbody>
                {% for vm in recent_vms %}
                <tr>
                    <td>{{ vm.name }}</td>
                    <td>{{ vm.data_source.name }}</td>
                    <td>{{ vm.last_seen|date:"Y-m-d H:i"|default:"—" }}</td>
                    <td>{% if vm.status == 'idle' %}<span class="badge badge-idle">{% trans "Idle" %}</span>{% elif vm.status == 'missing' %}<span class="badge badge-missing">{% trans "Missing" %}</span>{% elif vm.status == 'active' %}<span class="badge badge-active">{% trans "Active" %}</span>{% else %}<span style="color: var(--text-muted);">—</span>{% endif %}</td>
                    <td>{% if vm.idle_score is not None %}{{ vm.idle_score|floatformat:1 }}{% else %}—{% endif %}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
        {% if recent_scans %}
        <h3 class="section-title">{% trans "Recent scan runs" %}</h3>
        <table>
            <thead><tr><th>{% trans "Started" %}</th><th>{% trans "Source" %}</th><th>{% trans "Status" %}</th></tr></thead>
            <tbody>
                {% for run in recent_scans %}
                <tr><td>{{ run.started_at|date:"Y-m-d H:i" }}</td><td>{% if run.data_source %}{{ run.data_source.name }}{% else %}—{% endif %}</td><td>{{ run.get_status_display }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </main>
</body>
</html>
"""


@login_required(login_url="/accounts/login/")
def home(request):
    """Redirect root to the NOC dashboard."""
    return redirect("web:dashboard")
