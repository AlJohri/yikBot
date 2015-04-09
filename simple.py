import time
import pyak
import copy
import requests

from firebase import firebase
firebase = firebase.FirebaseApplication('https://aljohri-nuyak.firebaseio.com', None)

requests.packages.urllib3.disable_warnings()

# firebase.delete("/yaks", None)

def yak_to_dict(yak):
    yak_dict = copy.deepcopy(dict(yak.__dict__))
    yak_dict['client'] = yak.client.__dict__
    yak_dict['client']['location'] = yak_dict['client']['location'].__dict__ if type(yak_dict['client']['location']) != dict else yak_dict['client']['location']
    return yak_dict

yakker = pyak.Yakker(user_id='FFD35754D9024E83425053CB67B7C9D3')
print "New yakker registered with ID: %s" % yakker.id
locations = {
    "tech": pyak.Location(42.057796,-87.676634)
}

while True:
    yakker.update_location(locations['tech'])
    yaks = yakker.get_yaks()
    for yak in yaks:
        yak.message_id = yak.message_id.replace("R/", "")
        if firebase.get('/yaks', yak.message_id):
            # import pdb; pdb.set_trace()
            break
        result = firebase.put(url='/yaks', name=yak.message_id, data=yak_to_dict(yak), headers={'print': 'pretty'})
        print yak.time, yak.message_id, yak.message
    print "Sleep 10 seconds...."
    time.sleep(10)