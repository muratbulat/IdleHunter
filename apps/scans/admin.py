from django.contrib import admin
from .models import DataSource, ScanRun, VirtualMachine


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "is_enabled", "created_at")
    list_filter = ("source_type", "is_enabled")


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = (
        "name", "uuid", "data_source", "power_state", "last_seen",
        "status", "idle_score", "cpu_usage_percent", "memory_usage_mb",
    )
    list_filter = ("data_source", "status", "power_state")
    search_fields = ("name", "uuid")
    list_editable = ()  # optional: make status editable for overrides


@admin.register(ScanRun)
class ScanRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "finished_at", "status", "data_source")
    list_filter = ("status", "data_source")
