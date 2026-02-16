# apps.web.views - Secure enterprise dashboard (NOC / Command Center)
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from apps.scans.models import DataSource, VirtualMachine

# Idle threshold for "Idle/Zombie" count
IDLE_ZOMBIE_THRESHOLD = 0.7
# For donut: "Idle" = score >= 0.5; "Active" = score < 0.5 or None
IDLE_FOR_CHART = 0.5
# Data grid
PAGE_SIZE = 20
STATUS_ZOMBIE = "zombie"   # idle_score >= 0.8
STATUS_ACTIVE = "active"   # idle_score < 0.5
STATUS_POWERED_OFF = "powered_off"

# Sort: allowed GET "sort" values -> order_by field; default = idle_score desc
SORT_FIELDS = {
    "idle_score": "idle_score",      # Puan
    "name": "name",                   # Ad
    "source": "data_source__name",    # Kaynak
    "power_state": "power_state",     # Güç
    "last_seen": "last_seen",
}
DEFAULT_SORT = "idle_score"
DEFAULT_SORT_DIR = "desc"


@login_required(login_url="/accounts/login/")
def dashboard(request):
    """
    NOC-style dashboard: KPIs, charts, VM data grid with search, filter, pagination.
    """
    # KPI: Total VMs
    total_vms = VirtualMachine.objects.count()

    # KPI: Idle/Zombie VMs (idle_score > 0.7)
    idle_vms_qs = VirtualMachine.objects.filter(idle_score__gt=IDLE_ZOMBIE_THRESHOLD)
    idle_zombie_count = idle_vms_qs.count()

    # KPI: Potential savings
    savings_vcpu = 0
    savings_ram_mb = 0
    for vm in idle_vms_qs.only("metadata"):
        meta = vm.metadata or {}
        savings_vcpu += meta.get("numCpu") or 0
        savings_ram_mb += meta.get("memorySizeMB") or 0
    savings_ram_gb = round(savings_ram_mb / 1024.0, 1)

    # Chart A (Donut)
    active_count = VirtualMachine.objects.filter(
        Q(idle_score__lt=IDLE_FOR_CHART) | Q(idle_score__isnull=True)
    ).count()
    idle_for_donut = VirtualMachine.objects.filter(idle_score__gte=IDLE_FOR_CHART).count()
    chart_efficiency = {"active": active_count, "idle": idle_for_donut}

    # Chart B (Bar)
    top_sources_idle = (
        DataSource.objects.annotate(
            idle_count=Count("virtual_machines", filter=Q(virtual_machines__idle_score__gt=IDLE_ZOMBIE_THRESHOLD))
        )
        .filter(idle_count__gt=0)
        .order_by("-idle_count")[:5]
        .values_list("name", "idle_count")
    )
    chart_clusters = [{"label": name, "count": count} for name, count in top_sources_idle]

    # VM data grid: search, filter, order, paginate
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "all").strip().lower()
    if status not in ("all", STATUS_ZOMBIE, STATUS_ACTIVE, STATUS_POWERED_OFF):
        status = "all"

    sort_key = (request.GET.get("sort") or DEFAULT_SORT).strip().lower()
    sort_dir = (request.GET.get("dir") or DEFAULT_SORT_DIR).strip().lower()
    if sort_key not in SORT_FIELDS:
        sort_key = DEFAULT_SORT
    if sort_dir not in ("asc", "desc"):
        sort_dir = DEFAULT_SORT_DIR
    order_field = SORT_FIELDS[sort_key]
    order_prefix = "" if sort_dir == "asc" else "-"
    order_by = [f"{order_prefix}{order_field}", "-last_seen"]

    vm_queryset = (
        VirtualMachine.objects
        .select_related("data_source")
        .order_by(*order_by)
    )

    # Search: VM name, host name (data_source name)
    if q:
        vm_queryset = vm_queryset.filter(
            Q(name__icontains=q) | Q(data_source__name__icontains=q)
        )

    # Filter by status
    if status == STATUS_ZOMBIE:
        vm_queryset = vm_queryset.filter(idle_score__gte=0.8)
    elif status == STATUS_ACTIVE:
        vm_queryset = vm_queryset.filter(Q(idle_score__lt=0.5) | Q(idle_score__isnull=True))
    elif status == STATUS_POWERED_OFF:
        vm_queryset = vm_queryset.filter(power_state__icontains="poweredoff")

    paginator = Paginator(vm_queryset, PAGE_SIZE)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(int(page_number))
    except (ValueError, paginator.InvalidPage):
        page_obj = paginator.page(1)

    # Build query string for pagination/filter links (preserve q, status, sort, dir)
    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")
    query_string_suffix = query_params.urlencode()
    # Base query for sort links (exclude sort/dir so we can set them per column)
    query_params_no_sort = request.GET.copy()
    for k in ("page", "sort", "dir"):
        query_params_no_sort.pop(k, None)
    base_query_suffix = query_params_no_sort.urlencode()

    context = {
        "total_vms": total_vms,
        "idle_zombie_count": idle_zombie_count,
        "savings_vcpu": savings_vcpu,
        "savings_ram_gb": savings_ram_gb,
        "chart_efficiency": chart_efficiency,
        "chart_clusters": chart_clusters,
        "page_obj": page_obj,
        "current_q": q,
        "current_status": status,
        "current_sort": sort_key,
        "current_sort_dir": sort_dir,
        "query_params": query_params,
        "query_string_suffix": query_string_suffix,
        "base_query_suffix": base_query_suffix,
    }
    return render(request, "dashboard/index.html", context)
