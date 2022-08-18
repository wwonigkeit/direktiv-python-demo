import functions_framework
import logging
import json

# Original imports
from google.cloud import translate #required for the GCP Translation API
from google.oauth2 import service_account #required for the GCP Authentication API structure

def detect_language(text, location, project_id, gcpkey):
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
        return('{ errorcode: "com.tweetslang.error", errormsg: "{}}" }',e), 400
        # self._send_error("com.tweetslang.error",e)
        # sys.exit()

    # Display list of detected languages sorted by detection confidence.
    # The most probable language is first.
    for language in response.languages:
        # The Tweet we analysed 
        logging.info(RuntimeError("Return analysis for Twitter text"))
        # The language detected
        logging.info(RuntimeError("Language code: {}".format(language.language_code)))
        # Confidence of detection result for this language
        logging.info(RuntimeError("Confidence: {}".format(language.confidence)))
        return language.confidence, language.language_code

@functions_framework.http
def get_lang(request):
    reqData = request.get_json(silent=True)
    reqArgs = request.args
    
    # if reqData and all(key in reqData for key in ('searchstring', 'bearertoken', 'maxsearchreturns','outputfile')):
    if reqData:   
        # In this case, the data field of the Response returned is a list of Tweet
        # objects
        tweets = reqData['tweets']
        dicts = {}

        # Create an object with the tweets and the language in the format:
        logging.info(RuntimeError("Detecting languages for each tweet"))
        for tweet in tweets:
            # print(tweets[tweet][0])
            # print(tweet)
            language, confidence = detect_language(tweets[tweet][0],reqData['location'],reqData['projectid'],reqData['gcpkey'])
            dicts[tweet] = [tweets[tweet][0], language, confidence]

        logging.info(RuntimeError('Completed language detection'))
        # self.wfile.write(json.dumps(dictstop).encode())            
        return(json.dumps(dicts).encode()), 200

    else:
        #return self._send_error("com.tweetslang.error","json field 'searchstring', 'bearertoken', 'maxsearchreturns' and 'outputfile' must be set")
        return('{ errorcode: "com.tweetslang.error", errormsg: "json field \'tweets\', \'location\', \'gcpkey\' and \'outputfile\' must be set" }'), 400
