# Generated migration to remove unique constraint from matricula field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_replace_pedagogo_with_assistente_social'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudante',
            name='matricula',
            field=models.CharField(max_length=50, verbose_name='Matrícula'),
        ),
    ]
