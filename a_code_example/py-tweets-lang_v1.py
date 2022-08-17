# This is an example of a script that collects Tweets based on a filter input and then identifies the language in the Tweet.
# The script is dependent on internet connectivity and also on the Google Cloud Translatio credentials files available from:
#
import json
import sys, getopt
import tweepy #required for connecting to the Twitter API
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
        print("Google Translate API returned the following error:", e)
        sys.exit()

    # Display list of detected languages sorted by detection confidence.
    # The most probable language is first.
    for language in response.languages:
        # The Tweet we analysed 
        print("Twitter text: {}".format(text))
        # The language detected
        print("Language code: {}".format(language.language_code))
        # Confidence of detection result for this language
        print("Confidence: {}".format(language.confidence))
        return language.confidence, language.language_code

def main(argv):
    inputfile = ''
    outputfile = ''
    
    try:
        opts, args = getopt.getopt(argv,"i:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('py-tweets-lang.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('py-tweets-lang.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is ', inputfile)
    print('Output file is ', outputfile)

    try:
        config_file = open(inputfile, 'r')
    except OSError:
        print("Could not open/read file:", inputfile)
        sys.exit()

    with config_file:
        config_data = json.load(config_file)

    # Intialise all the variables we're going to use
    # Start with the Bearer Token for the Twitter API
    # Your app's bearer token can be found under the Authentication Tokens section
    # of the Keys and Tokens tab of your app, under the
    # Twitter Developer Portal Projects & Apps page at
    # https://developer.twitter.com/en/portal/projects-and-apps
    bearer_token = config_data['bearer_token']

    # Set up the Google Translate API requirements
    project_id = config_data['gcp_projectid']

    # Set up the search string you want to use
    twitter_searchstring = config_data['twitter_searchstring']

    # Set up the smaximum earch string quantity to return
    max_search_returns = config_data['max_search_returns']

    try:
        # Set up the authentication for Twitter
        client = tweepy.Client(bearer_token=bearer_token)

        # Search Recent Tweets
        # This endpoint/method returns Tweets from the last seven days
        response = client.search_recent_tweets(twitter_searchstring, max_results=max_search_returns)

    except tweepy.TweepyException as e:
        # Print the errors for the tweepy call
        print("Tweepy failed with the following error:",e)
        sys.exit(2)

    # In this case, the data field of the Response returned is a list of Tweet
    # objects
    tweets = response.data
    dicts = {}

    for tweet in tweets:
        language, confidence = detect_language(tweet.text,config_data['gcp_location'],config_data['gcp_projectid'],config_data['gcp_key'])
        dicts[tweet.id] = [tweet.text, language, confidence]

    # Dump the contents of the dictionary to a JSON file
    with open(outputfile, 'w') as fjson:
        json.dump(dicts, fjson, ensure_ascii=False, sort_keys=True, indent=3)

    print("Completed twitter scrape and language detection")

if __name__ == "__main__":
   main(sys.argv[1:])
