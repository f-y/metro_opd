# -*- coding: utf-8 -*-
from django.db import models


class BaseModel(models.Model):
    ld_context = models.CharField(max_length=255)
    ld_id      = models.CharField(max_length=127)
    ld_type    = models.CharField(max_length=63)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

