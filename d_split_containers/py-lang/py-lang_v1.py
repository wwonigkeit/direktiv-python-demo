# This is an example of a script that collects Tweets based on a filter input and then identifies the language in the Tweet.
# The script is dependent on internet connectivity and also on the Google Cloud Translatio credentials files available from:
#
# This script takes as an input a JSON object with the following structure:
# {
#    "projectid":"direktiv",
#    "location":"global",
#    "outputfile": "/tmp/output.json",
#    "gcpkey":
#    {
#       "type":"service_account",
#       "project_id":"direktiv",
#       "private_key_id":"<keyid>",
#       "private_key":"<key>",
#       "client_email":"<gcpemail>",
#       "client_id":"<gcpid>",
#       "auth_uri":"https://accounts.google.com/o/oauth2/auth",
#       "token_uri":"https://oauth2.googleapis.com/token",
#       "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
#       "client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/demo-translation-sa%40direktiv.iam.gserviceaccount.com"
#    },
#    "tweets":
#    {
#        "1559923789697277952": [
#            "Läste du detta 2018? \nJag gjorde det senare men det är omöjligt få folk att förstå att sossar och centerpartister tillsammans med andra partier utför skådespel.\n\n* Räcker det med en komprometterande minister som delar ut direktiv?\n\nhttps://t.co/ANTEvlsE3Q"
#        ],
#        "1559929015649161216": [
#            "RT @MarkusRosengren: 97% av befolkningen vill inte se MP i RD. Men nu har regeringspartiet gett direktiv att stödrösta på grön kommunism.…"
#        ],
#        "1559930431432232960": [
#            "RT @lindbergpolemik: Lise Nordin, energipolitisk talesperson för MP berättade i ett poddsamtal att man bytte ut folk i Vattenfalls styrelse…"
#        ],
#        "1559932963860668417": [
#            "@ejnermark @susannasilfver De hade ju redan bytt ut alla i vattenfalls styrelse som var för kärnkraft och gett tydliga direktiv vad som gällde om de ville sitta kvar.\nFör att inte tala om att MP skryter om att det var tack vare dem att kärnkraftverken lagts ner."
#        ]
#     }
# }
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json
import signal
import sys

# Original imports
from google.cloud import translate #required for the GCP Translation API
from google.oauth2 import service_account #required for the GCP Authentication API structure

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
    
    def _detect_language(self, text, location, project_id, gcpkey, actionID):
        # Create the authentication credentials for Google Translator
        json_acct_info = json.loads(json.dumps(gcpkey))
        
        try:
            credentials = service_account.Credentials.from_service_account_info(json_acct_info)
            scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])

            # Detecting the language of a text string
        
            client = translate.TranslationServiceClient(credentials=scoped_credentials)
            parent = f"projects/{project_id}/locations/{location}"

            response = client.detect_language(
                content=text,
                parent=parent,
                mime_type="text/plain",  # mime types: text/plain, text/html
            )
        except Exception as e:
            self._send_error("com.tweetslang.error",e)
            sys.exit()

        # Display list of detected languages sorted by detection confidence.
        # The most probable language is first.
        for language in response.languages:
            # The Tweet we analysed 
            self._log(actionID, "Return analysis for Twitter text")
            # The language detected
            self._log(actionID, "Language code: {}".format(language.language_code))
            # Confidence of detection result for this language
            self._log(actionID, "Confidence: {}".format(language.confidence))
            return language.confidence, language.language_code

    def do_POST(self):
        actionID = ""
        if DirektivActionIDHeader in self.headers:
            actionID = self.headers[DirektivActionIDHeader]
        else:
            return self._send_error("com.direktiv.header.error", "Header '%s' must be set" % DirektivActionIDHeader)

        self._log(actionID, "Decoding Input")
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        reqData = json.loads(self.data_string)
        
        if all(key in reqData for key in ('projectid','location','gcpkey','tweets','outputfile')):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # In this case, the data field of the Response returned is a list of Tweet
            # objects
            tweets = reqData['tweets']
            dicts = {}

            # Create an object with the tweets and the language in the format:
            self._log(actionID, "Detecting languages for each tweet")
            for tweet in tweets:
                print(tweets[tweet][0])
                print(tweet)
                language, confidence = self._detect_language(tweets[tweet][0],reqData['location'],reqData['projectid'],reqData['gcpkey'],actionID)
                dicts[tweet] = [tweets[tweet][0], language, confidence]

            try:
                # Dump the contents of the dictionary to a JSON file
                with open(reqData['outputfile'], 'w') as fjson:
                    json.dump(dicts, fjson, ensure_ascii=False, sort_keys=True, indent=3)
     
            except:
                # Print the errors for the tweepy call
                self._send_error("com.tweetslang.error",e)
                sys.exit(2)

            # Respond Data    
            self.wfile.write(json.dumps(dicts).encode())
            self._log(actionID, "Completed language detection")
            
            return
        else:
            return self._send_error("com.tweetslang.error","json field 'searchstring', 'bearertoken', 'projectid', 'location' and'gcpkey' must be set")

httpd = HTTPServer(('', PORT), DirektivHandler)
print('Starting twitter language server on ":%s"' % PORT)

def shutdown(*args):
    print('Shutting down Server')
    httpd.server_close()
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
httpd.serve_forever()