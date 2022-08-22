# This is an example of a script that collects Tweets based on a filter input and then identifies the language in the Tweet.
# The script is dependent on internet connectivity and also on the Google Cloud Translatio credentials files available from:
#
# This script takes as an input a JSON object with the following structure:
# {
#    "bearertoken":"<token>"
#    "location":"global",
#    "searchstring":"direktiv",
#    "maxsearchreturns": 20,
#    "outputfile": "/tmp/output.json"
# }
#
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json
import signal
import sys

# Original imports
import tweepy #required for connecting to the Twitter API

PORT = 8080

# Headers
DirektivActionIDHeader     = "Direktiv-ActionID"
DirektivErrorCodeHeader    = "Direktiv-ErrorCode"
DirektivErrorMessageHeader = "Direktiv-ErrorMessage"

class DirektivHandler(BaseHTTPRequestHandler):
    def _log(self, actionID, msg):
        if actionID != "development" and actionID != "Development":
            try:
                r = requests.post("http://localhost:8889/log?aid=%s" % actionID, headers={"Content-type": "plain/text"}, data = msg)
                if r.status_code != 200:
                    self._send_error("com.direktiv.logging.error", "log request failed to direktiv")
            except:
                self._send_error("com.direktiv.logging.error", "failed to log to direktiv")
        else: 
            print(msg)

    def _send_error(self, errorCode, errorMsg):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header(DirektivErrorCodeHeader, 'application/json')
        self.send_header(DirektivErrorMessageHeader, errorMsg)
        self.end_headers()
        self.wfile.write(json.dumps({"error": errorMsg}).encode())
        return

    def do_POST(self):
        actionID = ""
        if DirektivActionIDHeader in self.headers:
            actionID = self.headers[DirektivActionIDHeader]
        else:
            return self._send_error("com.direktiv.header.error", "Header '%s' must be set" % DirektivActionIDHeader)

        self._log(actionID, "Decoding Input")
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        reqData = json.loads(self.data_string)
        
        if all(key in reqData for key in ('searchstring', 'bearertoken', 'maxsearchreturns','outputfile')):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            try:
                # Set up the authentication for Twitter
                self._log(actionID, "Set up the authentication for Twitter")
                client = tweepy.Client(bearer_token=reqData['bearertoken'])

                # Search Recent Tweets
                # This endpoint/method returns Tweets from the last seven days
                response = client.search_recent_tweets(reqData['searchstring'], max_results=reqData['maxsearchreturns'])
                self._log(actionID, "Received a tweets from twitter")
            
            except tweepy.TweepyException as e:
                # Print the errors for the tweepy call
                self._send_error("com.tweetslang.error",e)
                sys.exit(2)

            # In this case, the data field of the Response returned is a list of Tweet
            # objects
            print(response.data)
            dicts = {}

            # Create an object with the tweets in JSON format:
            self._log(actionID, "Creating Tweet JSON object")
            for tweet in response.data:
                dicts[tweet.id] = [tweet.text]
            
            dictstop =  {}
            dictstop["tweets"] = dicts

            self.wfile.write(json.dumps(dictstop).encode())
            self._log(actionID, "Completed twitter scrape ")

            try:
                # Dump the contents of the dictionary to a JSON file
                with open(reqData['outputfile'], 'w') as fjson:
                    json.dump(dictstop, fjson, ensure_ascii=False, sort_keys=True, indent=3)
     
            except:
                # Print the errors for the tweepy call
                self._send_error("com.tweetslang.error",e)
                sys.exit(2)

            return
        else:
            return self._send_error("com.tweetslang.error","json field 'searchstring', 'bearertoken', 'maxsearchreturns' and 'outputfile' must be set")

httpd = HTTPServer(('', PORT), DirektivHandler)
print('Starting twitter get server on ":%s"' % PORT)

def shutdown(*args):
    print('Shutting down Server')
    httpd.server_close()
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
httpd.serve_forever()