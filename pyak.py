import base64
import hmac
import json
import requests
import time
import datetime
import urllib
import os
import re

from collections import OrderedDict

from hashlib import sha1
from hashlib import md5

from dateutil import tz

def parse_time(timestr):
    format = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.fromtimestamp(
        time.mktime(time.strptime(timestr, format))
    ).strftime('%Y-%m-%d %H:%M:%S')

class Location:
    def __init__(self, latitude, longitude, delta=None):
        self.latitude = latitude
        self.longitude = longitude
        if delta is None:
            delta = "0.030000"
        self.delta = delta

    def __str__(self):
        return "Location(%s, %s)" % (self.latitude, self.longitude)

class PeekLocation:
    def __init__(self, raw):
        self.id = raw['peekID']
        self.can_submit = bool(raw['canSubmit'])
        self.name = raw['location']
        lat = raw['latitude']
        lon = raw['longitude']
        d = raw['delta']
        self.location = Location(lat, lon, d)

class Comment:
    def __init__(self, raw, message_id, client):
        self.client = client
        self.message_id = message_id
        self.comment_id = raw["commentID"]
        self.comment = raw["comment"]
        self.time = parse_time(raw["time"])
        self.likes = int(raw["numberOfLikes"])
        self.poster_id = raw["posterID"]
        self.liked = int(raw["liked"])

        self.message_id = self.message_id.replace('\\', '')

    def upvote(self):
        if self.liked == 0:
            self.likes += 1
            self.liked += 1
            return self.client.upvote_comment(self.comment_id)

    def downvote(self):
        if self.liked == 0:
            self.likes -= 1
            self.liked += 1
            return self.client.downvote_comment(self.comment_id)

    def report(self):
        return self.client.report_comment(self.comment_id, self.message_id)

    def delete(self):
        if self.poster_id == self.client.id:
            return self.client.delete_comment(self.comment_id, self.message_id)

    def reply(self, comment):
        return self.client.post_comment(self.message_id, comment)

    def print_comment(self):
        my_action = ""
        if self.liked > 0:
            my_action = "^"
        elif self.liked < 0:
            my_action = "v"
        print ("\t\t%s(%s) %s \n\n\t\tPosted  %s" % (my_action, self.likes, self.comment, self.time))

from_zone = tz.gettz('GMT')
to_zone = tz.gettz('America/Chicago')

class Yak:
    def __init__(self, raw, client):
        self.client = client
        self.poster_id = raw["posterID"]
        self.hide_pin = bool(int(raw["hidePin"]))
        self.message_id = raw["messageID"]
        self.delivery_id = raw["deliveryID"]
        self.longitude = raw["longitude"]
        self.comments = int(raw["comments"])
        self.time = parse_time(raw["time"])
        self.latitude = raw["latitude"]
        self.likes = int(raw["numberOfLikes"])
        self.message = raw["message"]
        self.type = raw["type"]
        self.liked = int(raw["liked"])
        self.reyaked = raw["reyaked"]
        # import pdb; pdb.set_trace()
        self.gmt = datetime.datetime.utcfromtimestamp(raw['gmt']).replace(tzinfo=from_zone).astimezone(to_zone)

        #Yaks don't always have a handle
        try:
            self.handle = raw["handle"]
        except KeyError:
            self.handle = None

        #For some reason this seems necessary
        self.message_id = self.message_id.replace('\\', '')

    def upvote(self):
        if self.liked == 0:
            self.liked += 1
            self.likes += 1
            return self.client.upvote_yak(self.message_id)

    def downvote(self):
        if self.liked == 0:
            self.liked -= 1
            self.likes -= 1
            return self.client.downvote_yak(self.message_id)

    def report(self):
        return self.client.report_yak(self.message_id)

    def delete(self):
        if self.poster_id == self.client.id:
            return self.client.delete_yak(self.message_id)

    def add_comment(self, comment):
        return self.client.post_comment(self.message_id, comment)

    def get_comments(self):
        return self.client.get_comments(self.message_id)

    def get_locationNum(self):
        return self.latitude - self.longitude

    def print_yak(self):
        if self.handle is not None:
            print ("### %s ###" % self.handle)
        print ()
        print (self.message)
        print ("\n\t%s likes  |  Posted  %s  at  %s %s" % (self.likes, self.time, self.latitude, self.longitude))

class Yakker:
    base_url = "https://us-central-api.yikyakapi.net/api/"
    user_agent = "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-P5200 Build/JDQ39E)"
    HTTP_debugging = False;

    def __init__(self, user_id=None, location=None, force_register=False):
        if location is None:
            location = Location('0', '0')
        self.update_location(location)

        if user_id is None:
            user_id = self.gen_id()
            self.register_id_new(user_id)
        elif force_register:
            self.register_id_new(user_id)

        self.id = user_id

        self.handle = None

        #self.update_stats()

    def gen_id(self):
        x = md5(os.urandom(128)).hexdigest().upper()
        return x
        # return re.sub(r"(.{8})(.{4})(.{4})(.{4})(.{12})", r"\1-\2-\3-\4-\5", x)

    def register_id_new(self, id):
        params = {
            "userID": id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        result = self.get("registerUser", params)
        return result

    def sign_request(self, page, params):
        key = "35FD04E8-B7B1-45C4-9886-94A75F4A2BB4"

        #The salt is just the current time in seconds since epoch
        salt = str(int(time.time()))

        #The message to be signed is essentially the request, with parameters sorted
        msg = "/api/" + page
        sorted_params = list(params.keys())
        sorted_params.sort()
        if len(params) > 0:
            msg += "?"
        for param in sorted_params:
            msg += "%s=%s&" % (param, params[param])
        #Chop off last "&"
        if len(params) > 0:
            msg = msg[:-1]

        #the salt is just appended directly
        msg += salt

        #Calculate the signature
        h = hmac.new(key.encode(), msg.encode(), sha1)
        hash = base64.b64encode(h.digest())

        return hash, salt

    def post_sign_request(self, page, params):
        key = "35FD04E8-B7B1-45C4-9886-94A75F4A2BB4"

        #The salt is just the current time in seconds since epoch
        salt = str(int(time.time()))

        #The message to be signed is essentially the request, with parameters sorted
        msg = "/api/" + page

        #the salt is just appended directly
        msg += salt

        #Calculate the signature
        h = hmac.new(key.encode(), msg.encode(), sha1)
        hash = base64.b64encode(h.digest())

        return hash, salt


    def get(self, page, params):
        url = self.base_url + page

        params['version'] = '2.1.001'

        hash, salt = self.sign_request(page, params)
        params['hash'] = hash
        params['salt'] = salt

        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
        }

        fields = ["lat", "long", "userID", "version", "salt", "hash"]
        params = OrderedDict([(field, params[field]) for field in fields])

        # params = OrderedDict([(k,v) for k,v in params.iteritems() if k in fields])

        response = requests.get(url, params=params, headers=headers, verify=False)
        if (self.HTTP_debugging):
            print vars(response)
        return response

    def post(self, page, params):
        url = self.base_url + page

        params['version'] = '2.1.001'

        hash, salt = self.post_sign_request(page, params)
        getparams = {'hash': hash, 'salt': salt}

        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
        }

        response = requests.post(url, data=params, params=getparams, headers=headers, verify=False)
        if (self.HTTP_debugging):
            print vars(response)
        return response

    def enable_HTTP_debugging(self):
        self.HTTP_debugging = True
        return

    def disable_HTTP_debugging(self):
        self.HTTP_debugging = False
        return

    def get_yak_list(self, page, params):
        return self.parse_yaks(self.get(page, params).text)

    def parse_yaks(self, text):
        try:
            raw_yaks = json.loads(text)["messages"]
        except:
            raw_yaks = []
        yaks = []
        for raw_yak in raw_yaks:
            yaks.append(Yak(raw_yak, self))
        return yaks

    def parse_comments(self, text, message_id):
        try:
            raw_comments = json.loads(text)["comments"]
        except:
            raw_comments = []
        comments = []
        for raw_comment in raw_comments:
            comments.append(Comment(raw_comment, message_id, self))
        return comments

    def contact(self, message):
        params = {
            "userID": self.id,
            "message": message
        }
        return self.get("contactUs", params)

    def upvote_yak(self, message_id):
        params = {
            "userID": self.id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("likeMessage", params)

    def downvote_yak(self, message_id):
        params = {
            "userID": self.id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("downvoteMessage", params)

    def upvote_comment(self, comment_id):
        params = {
            "userID": self.id,
            "commentID": comment_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("likeComment", params)

    def downvote_comment(self, comment_id):
        params = {
            "userID": self.id,
            "commentID": comment_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("downvoteComment", params)

    def report_yak(self, message_id):
        params = params = {
            "userID": self.id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("reportMessage", params)

    def delete_yak(self, message_id):
        params = params = {
            "userID": self.id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("deleteMessage2", params)

    def report_comment(self, comment_id, message_id):
        params = {
            "userID": self.id,
            "commentID": comment_id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("reportMessage", params)

    def delete_comment(self, comment_id, message_id):
        params = {
            "userID": self.id,
            "commentID": comment_id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get("deleteComment", params)

    def get_greatest(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get_yak_list("getGreatest", params)

    def get_my_tops(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get_yak_list("getMyTops", params)

    def get_recent_replied(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get_yak_list("getMyRecentReplies", params)

    def update_location(self, location):
        self.location = location

    def get_my_recent_yaks(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get_yak_list("getMyRecentYaks", params)

    def get_area_tops(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get_yak_list("getAreaTops", params)

    def get_yaks(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.get_yak_list("getMessages", params)

    def post_yak(self, message, showloc=False, handle=False):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
            "message": message,
        }
        if not showloc:
            params["hidePin"] = "1"
        if handle and (self.handle is not None):
            params["hndl"] = self.handle
        return self.post("sendMessage", params)

    def get_comments(self, message_id):
        params = {
            "userID": self.id,
            "messageID": message_id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }

        return self.parse_comments(self.get("getComments", params).text, message_id)

    def post_comment(self, message_id, comment):
        params = {
            "userID": self.id,
            "messageID": message_id,
            "comment": comment,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        return self.post("postComment", params)

    def get_peek_locations(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        data = self.get("getMessages", params).json()
        peeks = []
        for peek_json in data['otherLocations']:
            peeks.append(PeekLocation(peek_json))
        return peeks

    def get_featured_locations(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        data = self.get("getMessages", params).json()
        peeks = []
        for peek_json in data['featuredLocations']:
            peeks.append(PeekLocation(peek_json))
        return peeks

    def get_yakarma(self):
        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
        }
        data = self.get("getMessages", params).json()
        return int(data['yakarma'])

    def peek(self, peek_id):
        if isinstance(peek_id, PeekLocation):
            peek_id = peek_id.id

        params = {
            "userID": self.id,
            "lat": self.location.latitude,
            "long": self.location.longitude,
            'peekID': peek_id,
        }
        return self.get_yak_list("getPeekMessages", params)