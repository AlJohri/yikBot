import pyak

yakker = pyak.Yakker()
print "New yakker registered with ID: %s" % yakker.id
# 42.059011, -87.676093
location = pyak.Location(42.049368, -87.682038)
yakker.update_location(location)
yaks = yakker.get_yaks()
for yak in yaks:
    print yak.time, yak.message_id, yak.message