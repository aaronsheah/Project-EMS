import webapp2
import datetime
from datetime import timedelta

##########################
# Jinja Template Setup
import os
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/views"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
##########################

from google.appengine.ext import ndb
from classes import Appliance
from classes import Power

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')

        ############### 24 Hour Total Consumption ###############
        now = datetime.datetime.now()
        period = now-timedelta(days=1)

        powerQry = Power.query(Power.added >= period).order(-Power.added)
        
        totalPowerReadings = [0 for i in range(24)]
        readingCounter = [0 for i in range(24)]

        for power in powerQry:
            time_difference = ((now - power.added).seconds)/60/60
            totalPowerReadings[time_difference] += power.real
            readingCounter[time_difference] += 1

        power_consumption = 0
        print totalPowerReadings
        for index, power in enumerate(totalPowerReadings):
            if power > 0:
                totalPowerReadings[index] /= readingCounter[index]
            power_consumption = power_consumption + power/1000
        print totalPowerReadings
        cost = "%.2f" % (power_consumption * 0.12360) # Last 30 Days Money Spent (https://www.eonenergy.com/~/media/PDFs/About-Us/price-matrix/v4s/EOn%20Fixed%201%20Year%20%20v4%202013%2007%2015.pdf)

        ######################################################
        applianceQry = Appliance.query().order(Appliance.name)
        applianceName = []
        appliancePowerReadings = []
        for appliance in applianceQry:
            tmpPowerQry = Power.query(Power.appliance == appliance.key, Power.added >= period).order(-Power.added)
            
            applianceName.append(appliance.name)
            
            tmpAppliancePowerReadings = 0
            for power in tmpPowerQry:
                tmpAppliancePowerReadings += power.real

            appliancePowerReadings.append(tmpAppliancePowerReadings)

        ######################################################

        params = {
            'home' : 1,
            'power_consumption' : "%.2f" % (power_consumption),
            'cost' : cost,
            'powerReadings' : totalPowerReadings,
            'applianceName' : applianceName,
            'appliancePowerReadings' : appliancePowerReadings
        }

        self.response.write(template.render(params))

class AppliancesHandler(webapp2.RequestHandler):
    def get(self):
        appliance_id = self.request.get('id')
        if appliance_id:
            template = JINJA_ENVIRONMENT.get_template('appliance_page.html')
            appliance = ndb.Key(urlsafe=appliance_id).get()
            params = {
                'appliance' : appliance,
            }
            self.response.write(template.render(params))
        else:
            template = JINJA_ENVIRONMENT.get_template('appliances.html')
            appliances = Appliance.query().order(Appliance.name)
            params = {
                'appliances' : appliances,
            }
            self.response.write(template.render(params))

class TestServerHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('test_server.html')
        params = {
            'testing' : 1
        }
        self.response.write(template.render(params))

class TestApplianceHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('test_appliance.html')
        params = {
            'testing' : 1
        }
        self.response.write(template.render(params))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/appliances', AppliancesHandler),
    ('/test_server', TestServerHandler),
    ('/test_appliance', TestApplianceHandler)
], debug=True)
