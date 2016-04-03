from google.appengine.ext import ndb

class Appliance(ndb.Model):
	name = ndb.StringProperty(required=True,indexed=True)
	category = ndb.StringProperty(required=True,indexed=True)

class Power(ndb.Model):
	added = ndb.DateTimeProperty(indexed=True)
	real = ndb.FloatProperty(indexed=False, required=True)
	apparent = ndb.FloatProperty(indexed=False)
	appliance = ndb.KeyProperty(indexed=True, kind=Appliance, required=True)