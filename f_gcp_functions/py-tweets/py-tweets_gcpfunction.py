import functions_framework
import logging
import json

# Original imports
import tweepy #required for connecting to the Twitter API

@functions_framework.http
def get_tweets(request):
    reqData = request.get_json(silent=True)
    reqArgs = request.args
    
    # if reqData and all(key in reqData for key in ('searchstring', 'bearertoken', 'maxsearchreturns','outputfile')):
    if reqData:
        try:
            # Set up the authentication for Twitter
            # self._log(actionID, "Set up the authentication for Twitter")
            logging.info(RuntimeError('Set up the authentication for Twitter'))
            client = tweepy.Client(bearer_token=reqData['bearertoken'])

            # Search Recent Tweets
            # This endpoint/method returns Tweets from the last seven days
            response = client.search_recent_tweets(reqData['searchstring'], max_results=reqData['maxsearchreturns'])
            # self._log(actionID, "Received a tweets from twitter")
            logging.info(RuntimeError('Received a tweets from twitter'))
        
        except tweepy.TweepyException as e:
            # Print the errors for the tweepy call
            # self._send_error("com.tweetslang.error",e)
            return('{errorcode: "com.tweetslang.error", errormsg: %}',e), 400

        # In this case, the data field of the Response returned is a list of Tweet
        # objects
        dicts = {}

        # Create an object with the tweets in JSON format:
        # self._log(actionID, "Creating Tweet JSON object")
        logging.info(RuntimeError('Creating Tweet JSON object'))
        for tweet in response.data:
            dicts[tweet.id] = [tweet.text]
        
        dictstop =  {}
        dictstop["tweets"] = dicts

        # self._log(actionID, "Completed twitter scrape ")
        logging.info(RuntimeError('Completed twitter scrape'))
        # self.wfile.write(json.dumps(dictstop).encode())            
        return(json.dumps(dictstop).encode()), 200
    else:
        #return self._send_error("com.tweetslang.error","json field 'searchstring', 'bearertoken', 'maxsearchreturns' and 'outputfile' must be set")
        return('{ errorcode: "com.tweetslang.error", errormsg: "json field \'searchstring\', \'bearertoken\', \'maxsearchreturns\' and \'outputfile\' must be set" }'), 400
