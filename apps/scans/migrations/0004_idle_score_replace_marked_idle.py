# Replace manual marked_idle with detected idle_score

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scans", "0003_virtualmachine_marked_idle"),
    ]

    operations = [
        migrations.AddField(
            model_name="virtualmachine",
            name="idle_score",
            field=models.FloatField(blank=True, db_index=True, null=True),
        ),
        migrations.RemoveField(
            model_name="virtualmachine",
            name="marked_idle",
        ),
    ]
