from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_userprofile_next_reset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='related_object_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Related Object ID'),
        ),
    ]
