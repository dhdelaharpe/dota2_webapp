from flask import Flask, render_template, jsonify, request 
from graphql_server.flask import GraphQLView
from mongoengine import connect
import sys 
sys.path.append('./handlers')
sys.path.append('./handlers/graphql')
from schema import schema 
import dbHandler as db 
import parseData as parse
import os 
import json

app = Flask(__name__)

with open('static/lang_en.json', 'r') as f: ### load localization file and add to config for access elsewhere. 
    localization_data=json.load(f)['Tokens']
localization_data = {key.lower():value for key,value in localization_data.items()} ### there are case mismatches in the file 
app.config['LOCALIZATION_DATA'] = localization_data


#graphql db connection
connect(
    db='dota2',
    host='localhost',
    port=27017
)
##connect db matches
dbM= db.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
dbM.connect(dbName='dota2',collectionName='matches')
dbH = db.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
dbH.connect(dbName='dota2',collectionName='heroes_live')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/tables')
def tables():
    return render_template('table.html')

@app.route('/api/radiant_win_rate_over_time',methods=['GET'])
def getRadiantWinRateOverTime():
    interval=request.args.get('interval','day')
    winRate = dbM.getWinRateOverTime(interval)
    return jsonify(winRate)

@app.route('/api/populate_hero_list',methods=['GET'])
def populateHeroList():
    heroes=dbH.searchData({},{"localized_name":1,"_id":0, "hero_id":1,"img_small":1,"img_full":1},sort=["localized_name",1])
    print(heroes)
    return jsonify(heroes)

@app.route('/api/hero_win_rate_over_time',methods=['GET'])
def getHeroWinRateOverTime():
    heroId = int(request.args.get('hero_id'))
    interval = request.args.get('interval','day')
    winRate = dbM.getHeroWinRateOverTime(interval,heroId)
    return jsonify(winRate)

@app.route('/api/populate_hero_table',methods=['GET'])
def populateHeroTable():
    #fetch args to filter with
    heroId = int(request.args.get('hero_id'))  # Convert heroId to an integer
    rankTier = request.args.get('avg_rank_tier')
    minPlayedOverall = int(request.args.get('min_played_overall'))
    minPlayedRadiant = int(request.args.get('min_played_radiant'))
    minPlayedDire = int(request.args.get('min_played_dire'))
    minWinrate = float(request.args.get('min_win_overall'))
    minWinrateRadiant = float(request.args.get('min_win_radiant'))
    minWinrateDire = float(request.args.get('min_win_dire'))

    winRatesMatchFilter= {'picks_bans.hero_id':heroId} #filter to just match the games where hero is picked or banned
    if(rankTier): #add it to match statement of pipeline
        league = int(rankTier)
        winRatesMatchFilter["avg_rank_tier"]={
            "$gt":league*10, #league = 1:8 *10 + 1:5 for tier in league
            "$lt":(1+league) *10 
        }

    getWinRatesQuery = [
        {
            '$match':winRatesMatchFilter
        }, 
        {
        '$addFields': {
            'won_radiant': {
                '$cond': {
                    'if': {
                        '$and': [
                            {
                                '$in': [
                                    heroId, '$radiant_team'
                                ]
                            }, '$radiant_win'
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }, 
            'won_dire': {
                '$cond': {
                    'if': {
                        '$and': [
                            {
                                '$in': [
                                    heroId, '$dire_team'
                                ]
                            }, {
                                '$eq': [
                                    '$radiant_win', False
                                ]
                            }
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }, 
            'games_radiant': {
                '$cond': {
                    'if': {
                        '$in': [
                            heroId, '$radiant_team'
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }, 
            'games_dire': {
                '$cond': {
                    'if': {
                        '$in': [
                            heroId, '$dire_team'
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }
        }
    }, {
        '$addFields': {
            'picked': {
                '$cond': {
                    'if': {
                        '$or': [
                            {
                                '$gt': [
                                    '$games_radiant', 0
                                ]
                            }, {
                                '$gt': [
                                    '$games_dire', 0
                                ]
                            }
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }
        }
    }, {
        '$addFields': {
            'banned': {
                '$cond': {
                    'if': {
                        '$gt': [
                            '$picked', 0
                        ]
                    }, 
                    'then': 0, 
                    'else': 1
                }
            }
        }
    }, {
        '$addFields': {
            'contested': {
                '$cond': {
                    'if': {
                        '$or': [
                            {
                                '$eq': [
                                    '$picked', heroId
                                ]
                            }, {
                                'eq': [
                                    '$banned', heroId
                                ]
                            }
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }
        }
    }, {
        '$group': {
            '_id': None, 
            'total_radiant_games': {
                '$sum': '$games_radiant'
            }, 
            'total_dire_games': {
                '$sum': '$games_dire'
            }, 
            'games_won_radiant': {
                '$sum': '$won_radiant'
            }, 
            'games_won_dire': {
                '$sum': '$won_dire'
            }, 
            'total_contested': {
                '$sum': '$contested'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'total_games': {
                '$sum': {
                    '$add': [
                        '$total_radiant_games', '$total_dire_games'
                    ]
                }
            }, 
            'total_wins': {
                '$add': [
                    '$games_won_radiant', '$games_won_dire'
                ]
            }, 
            'total_radiant_games': 1, 
            'games_won_radiant': 1, 
            'total_dire_games': 1, 
            'games_won_dire': 1, 
            'total_contested': 1, 
            'radiant_win_rate': {
                '$cond': {
                    'if': {
                        '$gt': [
                            '$total_radiant_games', 0
                        ]
                    }, 
                    'then': {
                        '$multiply': [
                            {
                                '$divide': [
                                    '$games_won_radiant', '$total_radiant_games'
                                ]
                            }, 100
                        ]
                    }, 
                    'else': 0
                }
            }, 
            'dire_win_rate': {
                '$cond': {
                    'if': {
                        '$gt': [
                            '$total_dire_games', 0
                        ]
                    }, 
                    'then': {
                        '$multiply': [
                            {
                                '$divide': [
                                    '$games_won_dire', '$total_dire_games'
                                ]
                            }, 100
                        ]
                    }, 
                    'else': 0
                }
            }
        }
    }, {
        '$project': {
            'total_wins': 1, 
            'total_games': 1, 
            'overall_win_rate': {
                '$cond': {
                    'if': {
                        '$gt': [
                            '$total_games', 0
                        ]
                    }, 
                    'then': {
                        '$multiply': [
                            {
                                '$divide': [
                                    '$total_wins', '$total_games'
                                ]
                            }, 100
                        ]
                    }, 
                    'else': 0
                }
            }, 
            'total_radiant_games': 1, 
            'total_dire_games': 1, 
            'games_won_radiant': 1, 
            'games_won_dire': 1, 
            'radiant_win_rate': 1, 
            'dire_win_rate': 1, 
            'total_contested': 1
        }
    },
        {
            '$match':{
                'total_games': {'$gte':minPlayedOverall},
                'overall_win_rate': {'$gte': minWinrate},
                'total_radiant_games': {'$gte': minPlayedRadiant},
                'total_dire_games': {'$gte': minPlayedDire},
                'radiant_win_rate': {'$gte': minWinrateRadiant},
                'dire_win_rate': {'$gte': minWinrateDire}
            }
        }
    ]

    winRates = dbM.getAggregate(getWinRatesQuery)
    if(winRates):
        return jsonify(winRates[0])
    else:
        return jsonify({})

@app.route('/api/matches_count',methods=['GET'])
def getMatchesCount():
    query= request.args.get('query',default='{}')
    avg_rank_tier = request.args.get('avg_rank_tier',default=None)
    try:
        query =json.loads(query) if query else {}
    except json.JSONDecodeError:
        return jsonify({"invalid query format"}),400
    query['detailed']={
        "$exists":True
    }
    if avg_rank_tier is not None:
        try:
            league = int(avg_rank_tier)
            query['avg_rank_tier']= {
                "$gt": league*10,
                "$lt": (1+league)*10
            }
        except ValueError:
            print("error invalid avg_rank_tier format")
    
    count = dbM.countEntries(query=query)
    return jsonify({"count":count})

app.add_url_rule('/api/graphql',view_func =GraphQLView.as_view('graphql', schema = schema, graphiql=True))
'''
@app.teardown_appcontext
def closeDbSession(exception=None):
    dbM.endSession()
'''
if __name__=="__main__":
    app.run(debug=True)