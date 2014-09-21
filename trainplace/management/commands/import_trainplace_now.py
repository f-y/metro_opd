# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from trainplace.models import TrainPlace

class Command(BaseCommand):

    def handle(self, *args, **options):
        TrainPlace.import_all()
