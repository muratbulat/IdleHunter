# IdleHunter REST API views (Swagger-documented)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.scans.models import VirtualMachine, DataSource


class VMPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


@swagger_auto_schema(method="get", responses={200: "OK"})
@api_view(["GET"])
@permission_classes([AllowAny])
def api_health(request):
    """Health check for load balancers and monitoring."""
    return Response({"status": "ok", "service": "IdleHunter"})


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("q", openapi.IN_QUERY, description="Search by VM or source name", type=openapi.TYPE_STRING),
        openapi.Parameter("status", openapi.IN_QUERY, description="Filter: all, zombie, active, powered_off", type=openapi.TYPE_STRING),
        openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_vm_list(request):
    """List virtual machines with optional search and filter."""
    from django.db.models import Q

    qs = VirtualMachine.objects.select_related("data_source").order_by("-idle_score", "-last_seen")
    q = (request.query_params.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(data_source__name__icontains=q))
    status_filter = (request.query_params.get("status") or "all").strip().lower()
    if status_filter == "zombie":
        qs = qs.filter(idle_score__gte=0.8)
    elif status_filter == "active":
        qs = qs.filter(Q(idle_score__lt=0.5) | Q(idle_score__isnull=True))
    elif status_filter == "powered_off":
        qs = qs.filter(power_state__icontains="poweredoff")

    paginator = VMPagination()
    page = paginator.paginate_queryset(qs, request)
    if page is not None:
        data = [
            {
                "id": vm.id,
                "name": vm.name,
                "uuid": vm.uuid,
                "data_source": vm.data_source.name if vm.data_source_id else None,
                "idle_score": vm.idle_score,
                "power_state": vm.power_state,
                "last_seen": vm.last_seen.isoformat() if vm.last_seen else None,
            }
            for vm in page
        ]
        return paginator.get_paginated_response(data)
    return Response([], status=status.HTTP_200_OK)


@swagger_auto_schema(method="get", responses={200: "OK", 404: "Not found"})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_vm_detail(request, pk):
    """Retrieve a single virtual machine by ID."""
    try:
        vm = VirtualMachine.objects.select_related("data_source").get(pk=pk)
    except VirtualMachine.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        "id": vm.id,
        "name": vm.name,
        "uuid": vm.uuid,
        "data_source": vm.data_source.name if vm.data_source_id else None,
        "idle_score": vm.idle_score,
        "power_state": vm.power_state,
        "last_seen": vm.last_seen.isoformat() if vm.last_seen else None,
        "last_boot_time": vm.last_boot_time.isoformat() if vm.last_boot_time else None,
        "status": vm.status,
    })


@swagger_auto_schema(method="get")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_data_sources(request):
    """List data sources (vCenter, Aria, Stor2RRD)."""
    sources = DataSource.objects.filter(is_enabled=True).values("id", "name", "source_type")
    return Response(list(sources))
