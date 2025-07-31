from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CVEEntry',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cve_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('information', models.TextField(blank=True)),
                ('date_created', models.DateField()),
                ('date_updated', models.DateField()),
                ('cve_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CVESource',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('provider', models.CharField(max_length=100)),
                ('interval', models.IntegerField()),
                ('timestamp_last', models.DateTimeField(blank=True, null=True)),
            ],
        )
    ]