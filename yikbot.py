import pyak
import time

class Yikbot(pyak.Yakker):
    yakkers = []

    def boot(self):
        while True:
            print "DEBUG: Scanning feed"
            yaks = self.get_yaks()
            for yak in yaks:
                if yak.message.startswith("@yikBot"):
                    print "DEBUG: Found a targeted yak"
                    self.respond(yak)
            print "DEBUG: Going to sleep, will repeat in 10 seconds"
            time.sleep(10)

    def respond(self, yak):
        yak.add_comment("Hi, I'm yikBot.\n--yB")

    def multi_upvote(self, message, count):
        yakkers = []
        for i in range(0, count):
            yakker = pyak.Yakker()
            print "DEBUG: Registered new user with id %s" % yakker.id
            yakker.update_location(self.location)
            yakkers.append(yakker)

        print "DEBUG: Going to sleep, new yakkers must wait ~90 seconds before they can act"
        time.sleep(90)
        print "DEBUG: Waking up and beginning scan"

        upvotes = 0
        for yakker in yakkers:
            print "DEBUG: yakker %s now scanning" % yakker.id
            yaks = yakker.get_yaks()
            for yak in yaks:
                if yak.message == message:
                    yak.upvote()
                    upvotes += 1
                    print "DEBUG: Upvoted yak %s times" % upvotes
                    break

    def premade_multi_upvote(self, message):
        upvotes = 0
        for yakker in self.yakkers:
            print "DEBUG: yakker %s now scanning" % yakker.id
            yaks = yakker.get_yaks()
            for yak in yaks:
                if yak.message == message:
                    yak.upvote()
                    upvotes += 1
                    print "DEBUG: Upvoted yak %s times" % upvotes
                    break


    def multi_downvote(self, message, count):
        yakkers = []
        for i in range(0, count):
            yakker = pyak.Yakker()
            print "DEBUG: Registered new user with id %s" % yakker.id
            yakker.update_location(self.location)
            yakkers.append(yakker)

        print "DEBUG: Going to sleep, new yakkers must wait ~90 seconds before they can act"
        time.sleep(90)
        print "DEBUG: Waking up and beginning scan"

        downvotes = 0;
        for yakker in yakkers:
            print "DEBUG: yakker %s now scanning" % yakker.id
            yaks = yakker.get_yaks()
            for yak in yaks:
                if yak.message == message:
                    yak.downvote()
                    downvotes += 1
                    print "DEBUG: Downvoted yak %s times" % downvotes
                    break

    def premade_multi_downvote(self, message):
        downvotes = 0
        for yakker in self.yakkers:
            print "DEBUG: yakker %s now scanning" % yakker.id
            yaks = yakker.get_yaks()
            for yak in yaks:
                if yak.message == message:
                    yak.downvote()
                    downvotes += 1
                    print "DEBUG: Downvoted yak %s times" % downvotes
                    break

    def create_yakkers(self, count, location):
        for i in range(0, count):
            yakker = pyak.Yakker()
            print "DEBUG: Registered new user with id %s" % yakker.id
            yakker.update_location(location)
            self.yakkers.append(yakker)

    def farm_yakkers(self, filename, count):
        file = open(filename + ".txt", "a")
        for i in range(0, count):
            yakker = pyak.Yakker()
            file.write(yakker.id)
            file.write("\n")
        file.close()

    def harvest_yakkers(self, filename, count, location):
        file = open(filename + ".txt", "r")
        for i in range(0, count):
            yakker_id = file.readline().rstrip('\n')
            print yakker_id
            yakker = pyak.Yakker(yakker_id, location, False)
            self.yakkers.append(yakker)
        file.close()

    def clear_yakkers(self):
        self.yakkers = []