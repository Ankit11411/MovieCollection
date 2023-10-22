from django.db import models


class AppBaseModel(models.Model):
    """
    The base model for every model.
    Make sure you inherit this while making models except User related models.
    """
    created = models.DateTimeField(auto_now_add=True, null=False)
    modified = models.DateTimeField(auto_now=True, null=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
