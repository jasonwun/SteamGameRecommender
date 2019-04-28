# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Game(models.Model):
    Name = models.TextField(max_length=200)
    Short_Description = models.TextField()
    Header_Image = models.TextField()
    SteamUrl = models.TextField()
    Publishers = models.TextField()
    Release_Date = models.DateField()
