from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0003_store_media"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="review_photos/"),
        ),
    ]
