import schedule 
import time 
import os
import argparse
import sys 
sys.path.append('./handlers')
import apiHandler
import dbHandler
import parseData 
import pymongo

def cyclePopulateMatches(logging=None, source="OpenDota",seqNum=None):
    '''populate dataset work loop - opendota public matches endpoint 
    ''params--
        logging: bool: enable logging
        source:str: options[OpenDota, Steam] default OpenDota
        seqNum: int: sequence number to use for steam call'''
    logger=None 
    if(logging==True):
        import logging
        logging.basicConfig(level=logging.NOTSET)
        logger=logging.getLogger(__name__)
    try:
    #setup 
        api = apiHandler.ApiHandler()
        db = dbHandler.dbHandler(os.getenv('MONGO_CONNECTION_STR'))
        parse = parseData.parseData()
        if(source=='Steam'):
            collectionName= 'matches_steam'
        else:
            collectionName='matches'
        db.connect(id='match_id',dbName='dota2',collectionName=collectionName)
        if(logger):
            logger.info('Connected to db: {} collection: {}'.format('dota2', collectionName))
        
        #request+parse
        if(source=="OpenDota"):
            data = api.sendRequest(api.fetchPublicMatches())
            if(logger):
                logger.info('Sent API request')
            parsed = parse.parsePublicMatchesOpenDota(data)
        elif(source=="Steam"):
            data = api.sendRequest(api.fetchMatchHistoryBySeqNum(**{"seqNum":seqNum, "matches_requested":200}))
            if(logger):
                logger.info('Sent Steam API request')
            parsed = parse.parseMatchesSteam(data)
        if(logger):
            logger.info('Parsed data')
        
        #insert + close 
        db.insertData(parsed,True)
        if(logger):
            logger.info('New data inserted to db')
        db.endSession()
        if(logger):
            logger.info('db connection closed')
        print("Task completed successfully")
    except Exception as err:
        print('Error occurred: {}'.format(err))

def getLatestSequenceNumber():
    '''check db for last steam sequence number added
    returns---
        seqNum: int''' 
    db = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
    db.connect(id="match_id",dbName="dota2",collectionName="matches_steam")
    filt = {"match_seq_num":1}
    sort = [('match_seq_num',pymongo.DESCENDING)]
    return db.findOne(filt,sort=sort)['match_seq_num']

def fetchDetails(api,db,matchId=None, matchSeqNum=None, logging=None):
    '''get details from steam endpoint of matchid ** endpoint down making workaround by using sequence number
    :params: api (apiHandler obj) instance to use
    :paraps: db (dbHandler obj) instance to use
    :params (int) matchid 
    :return (dict) response''' 
    #handle logging 
    logger=None 
    if(logging==True):
        import logging
        logging.basicConfig(level=logging.NOTSET)
        logger=logging.getLogger(__name__)
    try:
        if(matchSeqNum is not None):
            url = api.fetchMatchHistoryBySeqNum(**{"start_at_match_seq_num":matchSeqNum, "matches_requested":1}) #use sequence num endpoint but just request 1 game
            data = api.sendRequest(url)
            data=data['result']['matches'][0] #endpoint returns array of matches but we just want 1 for now -- TODO could increase data attainment by increasing request count here? 
            if(logger):
                logger.info("Successfully fetched match details using sequence number: {}".format(matchSeqNum))
        else:
            url = api.fetchMatchDetails(**{"match_id":matchId})
            data=api.sendRequest(url)
            if(logger):
                logger.info("Successfully fetched match details using match id: {}".format(matchId))
        return data 
    except KeyError as err:
        print("Key error: {}".format(err))
    except Exception as e:
        print("Error occured fetching details {}".format(e))
    return None 

import random 
def fillInData():
    ''' 
        TODO: unfinished
        function exists to find gaps in matchids/sequence numbers and fill them in -- will allow catching up to endpoints when app falls behind 
        :param api: apiHandler instance
        :param db: dbHandler instance connected to matches collection
        :param parser: parserData instance 
    '''
    api=apiHandler.ApiHandler()
    db = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
    db.connect(dbName='dota2', collectionName='matches')
    parse = parseData.parseData()
    #fetch ids 
    matchIds= db.searchData({},{'match_id':1,'match_seq_num':1, '_id':0},sort=['match_seq_num',1])
    #extract to list
    matchSequence= [match['match_seq_num'] for match in matchIds]
    #find gaps  -- iterate over ids, check if diff>1 then use range to populate gap
    def find_gaps(ids):
        missing_ids=[]
        for i in range(1,len(ids)):
            if ids[i]-ids[i-1]>1:
                missing_ids.extend(range(ids[i-1]+1, ids[i]))
        return missing_ids
    gap = find_gaps(matchSequence)
    print(f'found {len(gap)} missing matches')
    #data is currently mixture of opendota + steam as not all data is available on either
    #so to fetcha  new match we will have to fetch both 
    count=0
    iterate_through = random.sample(gap,250)
    for seq in iterate_through:
        try:
                
            url = api.fetchMatchHistoryBySeqNum(**{"start_at_match_seq_num":seq, "matches_requested":1}) 
            data = api.sendRequest(url)['result']['matches']
            parsed = parser.parsePublicMatches(data)[0]
            #this data will not have rank tier included which is essential to the application
            #query opendota for the match too -- note we did not have the matchId only the sequence number so we can't skip the first call 
            url = api.fetchMatch(parsed.get('match_id'))
            data = api.sendRequest(url)
            #now calculate avg rank tier and num_rank_tier 
            players = data.get('players',[])
            rank_tiers = [p.get('rank_tier') for p in players if p.get('rank_tier') is not None]
            if(len(rank_tiers)==0):
                print('no rank tiers available, continuing')
                continue
            avg_rank_tier = int(sum(rank_tiers)/len(rank_tiers))
            num_rank_tiers = max(rank_tiers)-min(rank_tiers)
    
        #consider stratz api as this has an endpoint for an array of matchids? 
        
            parsed['detailed']=True
            parsed['avg_rank_tier']= avg_rank_tier
            parsed['num_rank_tiers']=num_rank_tiers
            db.insertData(parsed,many=False)
            count=count+1
        except pymongo.errors.PyMongoError as err:
            print('DB error occured: {}'.format(err))
        except Exception as e:
            print(f'Exception: {e}')
    
    print(f'processed 250 attempts, filled in {count} new entries -- breaking to not overwhelm api endpoints')

def updateDetails(match,db):
    ''' handle preparing to merge with db
    :params match: (dict) returned match
    :params db: dbHandler instance connected to relevant collection
    '''
    try:
        seq_num = match["match_seq_num"]
        #we want the old duration as that has been parsed already so delete that entry
        del match["start_time"]
        match["detailed"]= True         #adding this to track which matches have been expanded to include full details 
        db.updateData(match,many=False, query={"match_seq_num":seq_num})
    except errors.PyMongoError as err:
        print("DB error occured: {}".format(err))
    except Exception as e:
        print("Exception : {}".format(e))


def mergeMatches(logging=None):
    '''check db for entries without details, fetch those details from steam api, merge into db '''
    logger=None 
    if(logging==True):
        import logging
        logging.basicConfig(level=logging.NOTSET)
        logger=logging.getLogger(__name__)
    try:
        #get matches to update
        db = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
        db.connect(dbName="dota2", collectionName="matches", id="match_id")
        matchesToExpand = db.findAll(filt={"detailed": {"$exists":False}}) # could also just filter for this value being true but may as well use mongo feature to make it slightly faster
        if(logger):
            logger.info("Found {} matches to update".format(db.collection.count_documents({"detailed":{"$exists":False}})))
        print("Found {} matches to update".format(db.collection.count_documents({"detailed":{"$exists":False}})))
        #make 1 API instance 
        api = apiHandler.ApiHandler()
        for match in matchesToExpand: #loop through and update each 
            seq_num = match.get("match_seq_num")
            if not seq_num:
                #perhaps add some indication through logger or print? 
                continue
            detailed = fetchDetails(api,db,matchSeqNum=seq_num) 
            updateDetails(detailed,db) #update entry 
            if(logger):
                logger.info("Updated match {}".format(match.get("match_id")))
        db.endSession()
        if(logger):
            logger.info("DB session closed")
        print("Detailed update task completed")
    except Exception as e:
        print("Exception occured : {}".format(e))

#handle input options to set scheduler
parser= argparse.ArgumentParser('E.g.')
parser.add_argument("--source",help="Source API to use: valid options:[Steam, OpenDota (default if none given)]",type=str,default="OpenDota",required=False, dest="source")
#parser.add_argument("--seqNum", help="Required for steamAPI, sequenceNumber to start from",type=int,default=None,required=False,dest="seqNum")
parser.add_argument("--logging",help="Enable logging, True/False",type=bool,default=False, required=False,dest="logging")
args = parser.parse_args()
source = args.source 
#seqNum = args.seqNum
logging = args.logging 

''' 
api=apiHandler.ApiHandler()
db = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
db.connect(dbName='dota2', collectionName='matches')
parse = parseData.parseData()
'''
#schedule tasks

if(source=='OpenDota'):
    schedule.every(10).minutes.do(cyclePopulateMatches,[logging,source])
    schedule.every(30).minutes.do(mergeMatches,logging)
    schedule.every(2).hours.do(fillInData)
    while True:
        schedule.run_pending()
        time.sleep(150)
        print('sleeping ...')
if(source=='Steam'):  ### TODO ::::this should match above
    while True:
        time.sleep(5)
        print('sleeping for 5 seconds')
        seqNum=getLatestSequenceNumber()
        print("current seqNum:{}".format(seqNum))
        cyclePopulateMatches(logging,source,seqNum)

