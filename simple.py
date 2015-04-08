import pyak

yakker = pyak.Yakker()
print "New yakker registered with ID: %s" % yakker.id
locations = {
	"tech": pyak.Location(42.057796,-87.676634)
}
yakker.update_location(locations['tech'])
yaks = yakker.get_yaks()
for yak in yaks:
    print yak.time, yak.message_id, yak.message