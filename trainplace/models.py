# -*- coding: utf-8 -*-
from django.db import models
from common.models import BaseModel
from common.utils import create_prm, request_metro, parse_response
from station.models import Station

import sys
import dateutil.parser as dp

class TrainPlace(BaseModel):
    date  = models.DateTimeField(db_index=True)
    valid = models.DateTimeField()
    delay = models.IntegerField()
    frequency = models.IntegerField()
    from_station = models.ForeignKey(Station, related_name='%(class)s_from', null=True, db_index=True)
    rail_direction = models.CharField(max_length=255)
    railway = models.CharField(max_length=255)
    starting_station = models.ForeignKey(Station, related_name='%(class)s_stating', null=True)
    terminal_station = models.ForeignKey(Station, related_name='%(class)s_terminal', null=True)
    to_station = models.ForeignKey(Station, related_name='%(class)s_to', null=True, db_index=True)
    train_number = models.CharField(max_length=31)
    train_owner = models.CharField(max_length=255)
    train_type = models.CharField(max_length=255)
    same_as = models.CharField(max_length=127)
    from_station_raw = models.CharField(max_length=255)
    starting_station_raw = models.CharField(max_length=255)
    terminal_station_raw = models.CharField(max_length=255)
    to_station_raw = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        index_together = [
            ['date', 'from_station', 'to_station'],
        ]

    def __unicode__(self):
        return u'%s %s (%s発 - %s行き): from %s - to %s' % (self.train_owner, self.train_number, 
                self.starting_station, self.terminal_station, self.from_station, self.to_station)

    RDF_TYPE = "odpt:Train"
    @classmethod
    def import_all(cls):
        prm = create_prm(cls.RDF_TYPE)
        res = request_metro(prm)
        data  = parse_response(res)
        
        instances = []
        for d in data:
            try:
                date = dp.parse(d['dc:date'])
                valid = dp.parse(d['dct:valid'])
                from_station = Station.get_or_create(d['odpt:fromStation'])
                starting_station = Station.get_or_create(d['odpt:startingStation'])
                terminal_station = Station.get_or_create(d['odpt:terminalStation'])
                to_station = Station.get_or_create(d['odpt:toStation'])

                cls(ld_context       = d['@context'],
                    ld_id            = d['@id'],
                    ld_type          = d['@type'],
                    date             = date,
                    valid            = valid,
                    delay            = d['odpt:delay'],
                    frequency        = d['odpt:frequency'],
                    from_station     = from_station,
                    rail_direction   = d['odpt:railDirection'],
                    railway          = d['odpt:railway'],
                    starting_station = starting_station,
                    terminal_station = terminal_station,
                    to_station       = to_station,
                    train_number     = d['odpt:trainNumber'],
                    train_owner      = d['odpt:trainOwner'],
                    train_type       = d['odpt:trainType'],
                    same_as          = d['owl:sameAs'],
                    from_station_raw  = d['odpt:fromStation'],
                    starting_station_raw  = d['odpt:startingStation'],
                    terminal_station_raw  = d['odpt:terminalStation'],
                    to_station_raw  = d['odpt:toStation'],
                    ).save()
            except:
                print sys.exc_info() 
                print d
                


