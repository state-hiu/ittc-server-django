import os
import sys
import httplib2
import base64
import math
import copy
import string
import datetime

import email.utils as eut

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.cache import cache, caches, get_cache
from django.http import Http404

from geojson import Polygon, Feature, FeatureCollection, GeometryCollection

from pymongo import MongoClient

from .stats import buildStats, incStats

import iso8601

import time

#from ittc.source.models import TileSource

http_client = httplib2.Http()


def clearLogs():
    client = MongoClient('localhost', 27017)
    db = client.ittc
    db.drop_collection(settings.LOG_REQUEST_COLLECTION)

def reloadLogs():
    clearLogs()

    log_root = settings.LOG_REQUEST_ROOT
    if log_root:
        log_files = glob.glob(log_root+os.sep+"requests_tiles_*.tsv")
        if log_files:
            client = MongoClient('localhost', 27017)
            db = client.ittc
            collection = db[settings.LOG_REQUEST_COLLECTION]
            for log_file in log_files:
                reloadLog(log_file,collection)


def reloadLog(path_file, collection):

    if path_file:
        if os.path.exists(path_file):
            lines = None
            with open(path_file,'r') as f:
                lines =  f.readlines()

            if lines:
                documents = []
                for line in lines:
                    values = line.rstrip('\n').split("\t")
                    status = values[0]
                    tileorigin = values[1]
                    tilesource = values[2]
                    z = values[3]
                    x = values[4]
                    y = values[5]
                    ip = values[6]
                    #dt = datetime.datetime.strptime(values[6],'YYYY-MM-DDTHH:MM:SS.mmmmmm')
                    dt = iso8601.parse_date(values[7])
                    location = z+"/"+x+"/"+y
                    r = buildTileRequestDocument(tileorigin, tilesource, x, y, z, status, dt, ip)
                    documents.append(r)
                    #collection.insert_one(r)
                #insert_many available in 3.0, which is still in Beta
                #collection.insert_many(documents, ordered=False)
                collection.insert(documents, continue_on_error=True)

def buildTileRequestDocument(tileorigin, tilesource, x, y, z, status, datetime, ip):
    r = {
        'ip': ip,
        'origin': tileorigin if tileorigin else "",
        'source': tilesource,
        'location': z+'/'+x+'/'+y,
        'z': z,
        'status': status,
        'year': datetime.strftime('%Y'),
        'month': datetime.strftime('%Y-%m'),
        'date': datetime.strftime('%Y-%m-%d'),
        'date_iso': datetime.isoformat()
    }
    return r

def logTileRequest(tileorigin,tilesource, x, y, z, status, datetime, ip):
    starttime = time.clock()
    #==#
    log_root = settings.LOG_REQUEST_ROOT
    #log_format = settings.LOG_REQUEST_FORMAT['tile_request']
    log_format = settings.LOG_REQUEST_FORMAT

    if log_root and log_format:
        if not os.path.exists(log_root):
            os.makedirs(log_root)

        log_file = log_root+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+".tsv"

        with open(log_file,'a') as f:
            line = log_format.format(status=status,tileorigin=tileorigin.name,tilesource=tilesource.name,z=z,x=x,y=y,ip=ip,datetime=datetime.isoformat())
            f.write(line+"\n")
            # Update MongoDB
            client = MongoClient('localhost', 27017)
            db = client.ittc
            r = buildTileRequestDocument(tileorigin.name,tilesource.name, x, y, z, status, datetime, ip)
            # Update Mongo Logs
            db[settings.LOG_REQUEST_COLLECTION].insert(r)
            # Update Mongo Aggregate Stats
            stats = buildStats(r)
            incStats(db, stats)

    print "Time Elapsed: "+str(time.clock()-starttime)