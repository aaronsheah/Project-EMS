import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

import logging

from google.appengine.ext import ndb
from classes import Power
from classes import Appliance

import datetime
from datetime import date, timedelta

################## Power Consumption Messages ##################
# Add Appliance ID
class PowerWrite(messages.Message):
 	appliance_id = messages.StringField(1)
 	real = messages.FloatField(2)
 	datetime = messages.IntegerField(3)

# Add Appliance ID
class PowerRequest(messages.Message):
	n = messages.IntegerField(1)
	appliance_id = messages.StringField(2)
	period = messages.IntegerField(3)

# Add Appliance ID
class PowerResponse(messages.Message):
	date = messages.StringField(1)
	real = messages.FloatField(2)

class ListOfPower(messages.Message):
	items = messages.MessageField(PowerResponse, 1, repeated=True)

class ConsumptionHistogramResponse(messages.Message):
	items = messages.FloatField(1, repeated=True)

################## Appliance Messages ##################
class ApplianceCreate(messages.Message):
	name = messages.StringField(1)
	category = messages.StringField(2)

class ApplianceResponse(messages.Message):
	name = messages.StringField(1)
	string_id = messages.StringField(2)
	category = messages.StringField(3)

class ListOfAppliance(messages.Message):
	items = messages.MessageField(ApplianceResponse, 1, repeated=True)

####################### EMS API #######################
@endpoints.api(name='ems', version='v1')
class EmsApi(remote.Service):

	################ Power Consumption Methods ################
	@endpoints.method(PowerWrite, PowerResponse,
		path='writePower', http_method='POST',
		name='power.writePower')
	def writePower(self, request):
		appliance = ndb.Key(Appliance, long(request.appliance_id)).get()
		if appliance:
			if request.datetime:
				added = datetime.datetime.fromtimestamp(request.datetime/1000.0)
			else:
				added = datetime.datetime.now()
			temp = Power(real=request.real, appliance=appliance.key, added = added)
			temp.put()

			power = PowerResponse(date=str(temp.added), real=temp.real)

			return power

	############################################################
	################## UNDER CONSTRUCTION ####################
	
	## Write Power Consumption Readings in a Batch (ie: Appliance id, array of power readings, array of datetime)
	# @endpoints.method(BatchPowerWrite, BatchPowerResponse,
	# 	path='writeBatchPower', http_method='POST',
	# 	name='power.writeBatchPower')
	# def writeBatchPower(self, request):
	# 	appliance = ndb.Key(Appliance, long(request.appliance_id)).get()
	# 	if appliance:
	# 		if request.datetime:
	# 			added = datetime.datetime.fromtimestamp(request.datetime/1000.0)
	# 		else:
	# 			added = datetime.datetime.now()
	# 		temp = Power(real=request.real, appliance=appliance.key, added = added)
	# 		temp.put()

	# 		power = PowerResponse(date=str(temp.added), real=temp.real)

	# 		return power
	################## UNDER CONSTRUCTION ####################
	############################################################

	# Method to get last N values for a particular appliance
	@endpoints.method(PowerRequest, ListOfPower,
		path='getNPower', http_method='POST',
		name='power.getNPower')
	def getNPower(self, request):
		if request.appliance_id:
			logging.info(request.appliance_id)
			appliance = ndb.Key(Appliance, long(request.appliance_id)).get()
			qry = Power.query(Power.appliance == appliance.key).order(-Power.added).fetch(request.n)
		else:
			qry = Power.query().order(-Power.added).fetch(request.n)
		
		powerReadings = []
		for power in qry:
			tmp_datetime = power.added.strftime('%Y-%m-%d %H:%M:%S.%f')
			tmp_datetime = tmp_datetime[:-3]
			powerReadings.append(PowerResponse(date=tmp_datetime, real=power.real))
		
		return ListOfPower(items=powerReadings)

	# Get List of Measurements from Past Day
	@endpoints.method(PowerRequest, ListOfPower,
		path='getDayConsumption', http_method='POST',
		name='power.getDayConsumption')
	def getDayConsumption(self, request):
		onedayago = datetime.datetime.now()-timedelta(days=1)
		if request.appliance_id:
			logging.info(request.appliance_id)
			appliance = ndb.Key(Appliance, long(request.appliance_id)).get()
			qry = Power.query(Power.appliance == appliance.key, Power.added >= onedayago).order(-Power.added)
		else:
			qry = Power.query(Power.added >= onedayago).order(-Power.added)
		
		powerReadings = []
		for power in qry:
			tmp_datetime = power.added.strftime('%Y-%m-%d %H:%M:%S.%f')
			tmp_datetime = tmp_datetime[:-3]
			powerReadings.append(PowerResponse(date=tmp_datetime, real=power.real))
		
		return ListOfPower(items=powerReadings)

	# Get the Power for the Day at Hour Intervals
	@endpoints.method(PowerRequest, ConsumptionHistogramResponse,
		path='getConsumptionHistogram', http_method='POST',
		name='power.getConsumptionHistogram')
	def getConsumptionHistogram(self, request):
		now = datetime.datetime.now()
		if request.period == 1:
			period = now-timedelta(days=1)
		else:
			period = now-timedelta(days=1)

		if request.appliance_id:
			logging.info(request.appliance_id)
			appliance = ndb.Key(Appliance, long(request.appliance_id)).get()
			qry = Power.query(Power.appliance == appliance.key, Power.added >= period).order(-Power.added)
		else:
			qry = Power.query(Power.added >= period).order(-Power.added)
		
		powerReadings = [0 for i in range(24)]
		for power in qry:
			time_difference = ((now - power.added).seconds)/60/60
			powerReadings[time_difference] += power.real

		logging.info(powerReadings)
		
		return ConsumptionHistogramResponse(items=powerReadings)

	##################### Appliance Methods #####################
	# Method to add new Appliance
	@endpoints.method(ApplianceCreate, ApplianceResponse,
		path='createAppliance', http_method='POST',
		name='appliance.createAppliance')
	def createAppliance(self, request):
		temp = Appliance(name=request.name, category=request.category)
		temp.put()

		appliance = ApplianceResponse(name=temp.name, string_id=str(temp.key.id()), category=temp.category)

		return appliance

	# Get user's appliances
	@endpoints.method(message_types.VoidMessage, ListOfAppliance,
		path='getAllAppliance', http_method='POST',
		name='appliance.getAllAppliance')
	def getAllAppliance(self, request):
		qry = Appliance.query().order()

		appliances = []
		for x in qry:
			appliances.append(ApplianceResponse(name=x.name, string_id=str(x.key.id()), category=x.category))

		return ListOfAppliance(items=appliances)
		
app = endpoints.api_server([EmsApi])