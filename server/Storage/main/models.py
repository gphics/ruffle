from django.db import models


class StorageManager(models.Model):

    key = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    folder = models.CharField(max_length=300)
    content_type = models.CharField(max_length=300)
    public_id = models.CharField(max_length=300)

    class Meta:
        db_table = "storage_manager"
