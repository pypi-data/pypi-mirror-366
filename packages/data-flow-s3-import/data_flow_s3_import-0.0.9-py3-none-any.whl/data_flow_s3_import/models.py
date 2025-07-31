from django.db import models


class IngestedModelManager(models.Manager):
    """
    Model manager that excludes missing/old imported records no longer found in the latest import file
    """

    def get_queryset(self):
        return super().get_queryset().filter(exists_in_last_import=True)


class ModelManager(models.Manager):
    """
    Generic model manager that includes the full dataset i.e. all records in DB, rather than just the last exported.
    """

    def get_queryset(self):
        return super().get_queryset()


class IngestedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    exists_in_last_import = models.BooleanField(default=True)

    objects = IngestedModelManager()
    include_all_objects = ModelManager()
