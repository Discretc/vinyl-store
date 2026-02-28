from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_review_photo"),
    ]

    operations = [
        # ordering is a state-only option, no SQL needed
        migrations.AlterModelOptions(
            name="review",
            options={"ordering": ["-createdDate"]},
        ),
        # The unique_together was never physically created in SQLite,
        # so we only update Django's migration state here.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="review",
                    unique_together=set(),
                ),
            ],
            database_operations=[],
        ),
    ]
