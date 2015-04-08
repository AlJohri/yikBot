import pyak

yakker = pyak.Yakker()
print "New yakker registered with ID: %s" % yakker.id
location = pyak.Location(42.059011, -87.676093)
yakker.update_location(location)
yaks = yakker.get_yaks()
for yak in yaks:
    print yak.message