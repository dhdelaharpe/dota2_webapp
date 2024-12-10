

def getRecentMatchesByHeroId(x,heroId, avgRankTier=8):
    '''
    :param x: (int) limit results
    :param avgRankTier: (int) elo tier 1-8 default 8 for "high elo"
    :param heroId: (int) Id of hero to filter for 
    '''
    query = [
        {
            "$match": {
                "avg_rank_tier": {'$gt':avgRankTier*10, '$lt':(1+avgRankTier)*10},  
                "players.hero_id": heroId  ,
                "detailed":True    
            }
        },
        {
            "$sort": {"match_seq_num": -1} #likely easier than using start_date and accounts for duration of games if at all relevant
        },
        {
            "$limit": x 
        },
        {
            "$unset":["_id"]
        }
    ]
    
    return query


def getAllHeroContestRate(avgRankTier=None):
    matchStage={} 
    if(avgRankTier is not None):
        matchStage['avg_rank_tier']={
            '$gt':avgRankTier*10,
            '$lt':(1+avgRankTier)*10
        }
    query = [ #use facet to get total_games pipeline and then aggregate for each hero 
            {
                '$match': matchStage
            }, {
                '$facet': {
                    'total_games': [
                        {
                            '$count': 'total_games'
                        }
                    ], 
                    'contested_heroes': [
                        {
                            '$unwind': '$picks_bans'
                        }, {
                            '$addFields': {
                                'is_contested': {
                                    '$or': [
                                        {
                                            '$eq': [
                                                '$picks_bans.is_pick', True
                                            ]
                                        }, {
                                            '$eq': [
                                                '$picks_bans.is_pick', False
                                            ]
                                        }
                                    ]
                                }
                            }
                        }, {
                            '$group': {
                                '_id': '$picks_bans.hero_id', 
                                'contested': {
                                    '$sum': {
                                        '$cond': [
                                            '$is_contested', 1, 0
                                        ]
                                    }
                                }
                            }
                        }
                    ]
                }
            }, {
                '$unwind': {
                    'path': '$total_games'
                }
            }, {
                '$project': {
                    'total_games': '$total_games.total_games', 
                    'contested_heroes': 1
                }
            }, {
                '$unwind': {
                    'path': '$contested_heroes'
                }
            }, {
                '$addFields': {
                    'hero_id': '$contested_heroes._id', 
                    'contested': '$contested_heroes.contested', 
                    'contest_rate': {
                        '$multiply': [
                            {
                                '$divide': [
                                    '$contested_heroes.contested', '$total_games'
                                ]
                            }, 100
                        ]
                    }
                }
            }, {
                '$project': {
                    'hero_id': 1, 
                    'contested': 1, 
                    'total_games': 1, 
                    'contest_rate': 1
                }
            }
        ]
    return query

def getHeroContestRate(heroId,avgRankTier):
    matchStage={}
    if(avgRankTier is not None):
        matchStage['avg_rank_tier']={
            '$gt': avgRankTier*10, 
            '$lt': (1+avgRankTier) *10
        }
    query = [
        {
            '$match': matchStage
        }, {
            '$project': {
                '_id': 1, 
                'picks_bans': 1
            }
        }, {
            '$addFields': {
                'pick_ban': {
                    '$in': [
                        heroId, {'$ifNull':['$picks_bans.hero_id',[]]}
                    ]
                }
            }
        }, {
            '$group': {
                '_id': heroId, 
                'contested': {
                    '$sum': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$pick_ban', True
                                ]
                            }, 1, 0
                        ]
                    }
                }, 
                'total_games': {
                    '$sum': 1
                },
            }
        }
    ]
    return query
def getLeaversQuery():
    leavers = {
                '$not': {
                    '$elemMatch': {
                        'leaver_status': {'$gte': 2}
                    }
                }
            }
    return leavers
def getWinRatesQuery(rankTier=None, minPlayedOverall=0, minPlayedRadiant=0,minPlayedDire=0,minWinrate=0,minWinrateRadiant=0,minWinrateDire=0):
    '''defaults at 0 and no rank tier, builds aggregation query '''

    matchStage={}
    if(rankTier): #add it to match statement of pipeline
        league = int(rankTier)
        matchStage["avg_rank_tier"]={
            "$gt":league*10, #league = 1:8 *10 + 1:5 for tier in league
            "$lt":(1+league) *10 
        }
    matchStage['players'] = getLeaversQuery()
      

    getWinRatesQuery = [
        {
            '$match':matchStage
        },

        {
            '$project': {
                'hero_id': {
                    '$concatArrays': [
                        '$radiant_team', '$dire_team'
                    ]
                }, 
                'radiant_win': 1, 
                'radiant_team': 1, 
                'dire_team': 1
            }
        }, {
            '$unwind': {
                'path': '$hero_id'
            }
        }, {
            '$addFields': {
                'is_radiant_hero': {
                    '$in': [
                        '$hero_id', '$radiant_team'
                    ]
                }, 
                'is_dire_hero': {
                    '$in': [
                        '$hero_id', '$dire_team'
                    ]
                }, 
                'hero_won': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {
                                    '$in': [
                                        '$hero_id', '$radiant_team'
                                    ]
                                }, '$radiant_win'
                            ]
                        }, 
                        'then': 1, 
                        'else': {
                            '$cond': {
                                'if': {
                                    '$and': [
                                        {
                                            '$in': [
                                                '$hero_id', '$dire_team'
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
                        }
                    }
                }
            }
        }, {
            '$addFields': {
                'radiant_played': {
                    '$cond': [
                        '$is_radiant_hero', 1, 0
                    ]
                }, 
                'dire_played': {
                    '$cond': [
                        '$is_dire_hero', 1, 0
                    ]
                }, 
                'radiant_win': {
                    '$cond': [
                        {
                            '$and': [
                                '$is_radiant_hero', '$hero_won'
                            ]
                        }, 1, 0
                    ]
                }, 
                'dire_win': {
                    '$cond': [
                        {
                            '$and': [
                                '$is_dire_hero', '$hero_won'
                            ]
                        }, 1, 0
                    ]
                }
            }
        }, {
            '$group': {
                '_id': '$hero_id', 
                'total_games': {
                    '$sum': 1
                }, 
                'total_wins': {
                    '$sum': '$hero_won'
                }, 
                'radiant_games': {
                    '$sum': '$radiant_played'
                }, 
                'radiant_wins': {
                    '$sum': '$radiant_win'
                }, 
                'dire_games': {
                    '$sum': '$dire_played'
                }, 
                'dire_wins': {
                    '$sum': '$dire_win'
                }
            }
        }, {
            '$addFields': {
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
                'radiant_win_rate': {
                    '$cond': {
                        'if': {
                            '$gt': [
                                '$radiant_games', 0
                            ]
                        }, 
                        'then': {
                            '$multiply': [
                                {
                                    '$divide': [
                                        '$radiant_wins', '$radiant_games'
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
                                '$dire_games', 0
                            ]
                        }, 
                        'then': {
                            '$multiply': [
                                {
                                    '$divide': [
                                        '$dire_wins', '$dire_games'
                                    ]
                                }, 100
                            ]
                        }, 
                        'else': 0
                    }
                }
            }
        }, {
            '$match': {
                'total_games': {
                    '$gte': minPlayedOverall
                },
                'overall_win_rate': {
                    '$gte': minWinrate
                },
                'radiant_games': {
                    '$gte': minPlayedRadiant
                },
                'dire_games': {
                    '$gte': minPlayedDire
                },
                'radiant_win_rate': {
                    '$gte': minWinrateRadiant
                },
                'dire_win_rate': {
                    '$gte': minWinrateDire
                },
            }
        },{
        "$project": {
            "_id":0,
            "hero_id": "$_id",
            "total_games":1,
            "total_wins":1,
            "radiant_games":1,
            "radiant_wins":1,
            "dire_games":1,
            "dire_wins":1,
            "overall_win_rate":1,
            "radiant_win_rate":1,
            "dire_win_rate":1
            }
        }
    ]
    return getWinRatesQuery

    

