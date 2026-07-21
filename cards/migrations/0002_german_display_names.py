from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('cards', '0001_initial')]

    operations = [
        migrations.AlterModelOptions(name='business', options={'verbose_name': 'Betrieb', 'verbose_name_plural': 'Betriebe'}),
        migrations.AlterModelOptions(name='venue', options={'ordering': ['position', 'name'], 'verbose_name': 'Bereich', 'verbose_name_plural': 'Bereiche'}),
        migrations.AlterModelOptions(name='businesssettings', options={'verbose_name': 'Anwendungseinstellung', 'verbose_name_plural': 'Anwendungseinstellungen'}),
        migrations.AlterModelOptions(name='membership', options={'verbose_name': 'Zugriffsrolle', 'verbose_name_plural': 'Zugriffsrollen'}),
        migrations.AlterModelOptions(name='customerprofile', options={'verbose_name': 'Kundenprofil', 'verbose_name_plural': 'Kundenprofile'}),
        migrations.AlterModelOptions(name='wallet', options={'ordering': ['display_name'], 'verbose_name': 'Guthabenkonto', 'verbose_name_plural': 'Guthabenkonten'}),
        migrations.AlterModelOptions(name='paymentrequest', options={'verbose_name': 'Zahlungsanforderung', 'verbose_name_plural': 'Zahlungsanforderungen'}),
        migrations.AlterModelOptions(name='ledgerentry', options={'ordering': ['-created_at'], 'verbose_name': 'Buchung', 'verbose_name_plural': 'Buchungen'}),
        migrations.AlterModelOptions(name='offer', options={'ordering': ['-created_at'], 'verbose_name': 'Angebot', 'verbose_name_plural': 'Angebote'}),
        migrations.AlterModelOptions(name='notification', options={'ordering': ['-created_at'], 'verbose_name': 'Mitteilung', 'verbose_name_plural': 'Mitteilungen'}),
        migrations.AlterModelOptions(name='pushdevice', options={'verbose_name': 'Endgerät', 'verbose_name_plural': 'Endgeräte'}),
        migrations.AlterField(
            model_name='membership',
            name='role',
            field=models.CharField(choices=[('OWNER', 'Inhaber'), ('MANAGER', 'Leitung'), ('STAFF', 'Mitarbeiter')], max_length=12),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='tier',
            field=models.CharField(choices=[('BEACH', 'Strand'), ('SUNSET', 'Sonnenuntergang'), ('SKYLINE', 'Panorama')], default='BEACH', max_length=12),
        ),
        migrations.AlterField(
            model_name='paymentrequest',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Wartet auf Bestätigung'), ('CONFIRMED', 'Bezahlt'), ('CANCELLED', 'Storniert')], default='PENDING', max_length=12),
        ),
        migrations.AlterField(
            model_name='offer',
            name='target',
            field=models.CharField(choices=[('ALL', 'Alle Mitglieder'), ('BEACH', 'Strand-Mitglieder'), ('SUNSET', 'Sonnenuntergang-Mitglieder'), ('SKYLINE', 'Panorama-Mitglieder')], default='ALL', max_length=12),
        ),
        migrations.AlterField(
            model_name='pushdevice',
            name='platform',
            field=models.CharField(choices=[('IOS', 'iOS'), ('ANDROID', 'Android'), ('WEB', 'Web-Anwendung')], max_length=12),
        ),
    ]
