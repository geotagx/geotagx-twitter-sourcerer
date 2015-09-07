from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import json, base64, urllib2
from settings import GEOTAGX_SOURCERER_TYPE, CATEGORIES, TARGET_HOST, TARGET_URI, DATABASE_SYNC, GEOTAGX_FILTER, consumer_key, consumer_secret, access_token,access_token_secret
import schedule
import time

DATA_DUMP = {}

class GeotagXTweetListener(StreamListener):
    def on_data(self, data):
        try:
            data = json.loads(data)
            if 'media' in data['entities'].keys():
                media_objects = data['entities']['media']
                for media_object in media_objects:
                    if media_object['type'] == 'photo':
                        media_object['tweet_created_at'] = data['created_at']
                        geotagx_harvestor(media_object)
            return True
        except Exception as err:
            """
                In case of any errors like UnicodeParse error,etc, just move onto the next data point
                TODO : Has to be handled more smartly
            """
            pass
            #print err

    def on_error(self, status):
        pass


def init():
    try:
        print "Reading list of known images from backup...."
        f = open("data_dump.json", "r")
        DATA_DUMP  = json.loads(f.read())
        f.close()
    except:
        print "Unable to read list of known images. Reseting database.."
        DATA_DUMP = {}

def backup():
    print "Taking backup of known images...."
    if len(DATA_DUMP.keys()) != 0:
        f = open("data_dump.json", "w")
        f.write(json.dumps(DATA_DUMP))
        f.close()

def geotagx_harvestor(media_object):
    image_url = media_object['media_url']
    source_uri = media_object['expanded_url']
    create_time = media_object['tweet_created_at']
    id_str = media_object['id_str']

    try:
        foo = DATA_DUMP[image_url]
        #if the image does not exist, the control should move to the exception block
        print "Duplicate image found, ignoring.....", image_url
    except:
        # Create Object for pushing to geotagx-sourcerer-proxy
        print "Pushing image to geotagx-sourcerer-proxy : ", image_url
        _sourcerer_object = {}
        _sourcerer_object['source'] = GEOTAGX_SOURCERER_TYPE
        _sourcerer_object['type'] = "IMAGE_SOURCE"
        _sourcerer_object['categories'] = CATEGORIES
        _sourcerer_object['image_url'] = image_url
        _sourcerer_object['source_uri'] = source_uri
        _sourcerer_object['create_time'] =create_time
        _sourcerer_object['id'] = id_str

        # Push data via geotagx-sourcerer-proxy
        ARGUMENTS = base64.b64encode(json.dumps(_sourcerer_object))
        GEOTAGX_SOURCERER_PROXY_URL = TARGET_HOST+TARGET_URI+"?sourcerer-data="+ARGUMENTS;
        try:
            urllib2.urlopen(GEOTAGX_SOURCERER_PROXY_URL)
            print "SUCCESSFULLY PUSHED : ", image_url
            DATA_DUMP[image_url] = _sourcerer_object
        except:
            print "FAILURE", image_url

        schedule.run_pending()

if __name__ == '__main__':
    init()
    schedule.every(DATABASE_SYNC).seconds.do(backup)
    l = GeotagXTweetListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=GEOTAGX_FILTER)


