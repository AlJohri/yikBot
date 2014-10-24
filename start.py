import pyak
import yikbot
import time

yb = yikbot.YikBot()

# Latitude and Longitude of location where bot should be localized
ybLocation = pyak.Location("42.275293", "-83.738609")
yb.update_location(ybLocation)
print "DEBUG: Registered yikBot with handle %s and id %s" % (yb.handle, yb.id)

print "DEBUG: Going to sleep, new yakkers must wait ~90 seconds before they can act"
time.sleep(90)

print "DEBUG: yikBot instance 90 seconds after initialization"
print vars(yb)

yb.boot()