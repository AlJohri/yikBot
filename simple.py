import pyak

yakker = pyak.Yakker()
print "New yakker registered with ID: %s" % yakker.id
# 41.849994, -87.650006
# lat	41.849994
# long	-87.650006
location = pyak.Location(41.849994, -87.650006)
yakker.update_location(location)
yaks = yakker.get_yaks()
for yak in yaks:
    print yak.time, yak.message_id, yak.message