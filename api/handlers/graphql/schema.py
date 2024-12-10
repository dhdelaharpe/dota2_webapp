import graphene
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from graphene.relay import Node
from models import Hero, Match, Abilities, HeroStats, HeroPickBanRate,AdditionalUnit, Abilities,PickBan,AbilityUpgrade, Player, Item, Attribute, Ability
import pipelines
from bson import ObjectId
from flask import current_app 
import utils

import logging


logging.basicConfig(level=logging.INFO)

class HeroType(MongoengineObjectType):
    class Meta:
        model = Hero
        interfaces = (Node,)

class HeroStatsType(MongoengineObjectType):
    class Meta:
        model=HeroStats
        interfaces=(Node,)

class HeroPickBanRateType(MongoengineObjectType):
    class Meta:
        model=HeroPickBanRate 
        interfaces = (Node,)
class AbilitiesType(MongoengineObjectType):
    class Meta:
        model = Abilities
        interfaces = (Node,)

class AdditionalUnitType(MongoengineObjectType):
    class Meta:
        model=AdditionalUnit
        interfaces=(Node,)

class AbilityUpgradeType(MongoengineObjectType):
    class Meta:
        model=AbilityUpgrade
        interfaces=(Node,)
class PickBanType(MongoengineObjectType):
    class Meta:
        model=PickBan
        interfaces=(Node,)

class PlayerType(MongoengineObjectType):
    class Meta:
        model=Player
    account_id=graphene.BigInt()
    additional_units = graphene.List(AdditionalUnitType)
    ability_upgrades = graphene.List(AbilityUpgradeType)

class MatchType(MongoengineObjectType):
    class Meta:
        model = Match
        interfaces = (Node,)
    match_id = graphene.BigInt()
    match_seq_num=graphene.BigInt()
    picks_bans = graphene.List(PickBanType)
    players= graphene.List(PlayerType)

class AbilityType(MongoengineObjectType):
    class Meta:
        model=Ability
        interfaces = (Node,)

class AttributeType(MongoengineObjectType):
    class Meta:
        model=Attribute
        interfaces= (Node,)

class ItemType(MongoengineObjectType):
    class Meta:
        model= Item
        interfaces=(Node,)
    
#added some localization to these queries, should likely move them all into a step when populating db, however, currently db is populated from various sources so that data is not all available at the time
class Query(graphene.ObjectType):
    # Heroes
    all_heroes = graphene.List(HeroType)
    hero_by_name = graphene.Field(HeroType, name=graphene.String(required=True))


    def resolve_all_heroes(self, info):
        ''' 
        using a utility to correctly index the objects here as GC was removing ref 
        '''
        localization = current_app.config['LOCALIZATION_DATA']
        heroes = Hero.objects.all()
        for hero in heroes:
            abilities = Abilities.objects(hero_id=hero.hero_id).first() 
            if abilities:
                for facet_key in hero.facets:
                    attr_path = ['facets', facet_key]
                    facet_value = utils.get_nested_attr(hero, attr_path)
                    if facet_value:
                        trans = utils.map_localization_for_ability(facet_key, localization, abilities['abilities'], abilities['talents'])
                        utils.get_nested_attr(hero, attr_path)['tooltip'] = trans

        return heroes

    def resolve_hero_by_name(self, info, name):
        return Hero.objects(name=name).first()

    hero_contest = graphene.Field(
        HeroPickBanRateType,
        hero_id = graphene.Int(),
        avg_rank_tier = graphene.Int(default_value=None)
    )
    def resolve_hero_contest(self,info,hero_id,avg_rank_tier=None):
        query = pipelines.getHeroContestRate(hero_id,avg_rank_tier)
        result = list(Match.objects.aggregate(query))[0]
        
        return HeroPickBanRateType(
            hero_id=hero_id,
            contested=result.get('contested'),
            total_games = result.get('total_games'),
            contest_rate = result.get('contested')/result.get('total_games')*100
        )
    all_hero_contest = graphene.List(
        HeroPickBanRateType,
        avg_rank_tier = graphene.Int(default_value=None)
    )
    def resolve_all_hero_contest(self,info,avg_rank_tier=None):
        query = pipelines.getAllHeroContestRate(avg_rank_tier)     
        results = list(Match.objects.aggregate(query))

        formattedResults = [
            HeroPickBanRateType(
                hero_id=res.get('hero_id'),
                contested=res.get('contested'),
                total_games = res.get('total_games'),
                contest_rate=res.get('contest_rate')
            ) for res in results
        ]

        return formattedResults
    # Matches
    all_matches = graphene.List(MatchType)
    match_by_id = graphene.Field(MatchType, match_id=graphene.BigInt(required=True))
    match_by_seq_num = graphene.Field(MatchType, match_seq_num=graphene.BigInt(required=True))

    def resolve_all_matches(self, info):
        return Match.objects.all()

    def resolve_match_by_id(self, info, match_id):
        return Match.objects(match_id=match_id).first()  # Use first() to handle missing records safely

    def resolve_match_by_seq_num(self, info, match_seq_num):
        return Match.objects(match_seq_num=match_seq_num).first()  # Use first() to handle missing records safely
   
    match_elo_sample = graphene.List(
        MatchType,
        avg_rank_tier = graphene.Int(default_value=8),
        hero_id = graphene.Int(default_value=1),
        limit = graphene.Int(default_value=10)
    )
    def resolve_match_elo_sample(self,info,hero_id,avg_rank_tier,limit=10):#could use pipelines to hold the query
        query = pipelines.getRecentMatchesByHeroId(limit,hero_id,avg_rank_tier)
        results = list(Match.objects.aggregate(query))
        formattedResults = []

        for result in results:
            match_id = result.get('match_id')  
            try:                
                picks_bans = result.get('picks_bans', [])
                if picks_bans is None:
                    picks_bans = []
                players = result.get('players', [])
                if players is None:
                    players = []

                match_data = MatchType(
                    match_id=match_id,
                    match_seq_num=result.get('match_seq_num'),
                    radiant_win=result.get('radiant_win'),
                    start_time=result.get('start_time'),
                    duration=result.get('duration'),
                    lobby_type=result.get('lobby_type'),
                    game_mode=result.get('game_mode'),
                    avg_rank_tier=result.get('avg_rank_tier'),
                    num_rank_tier=result.get('num_rank_tier'),
                    cluster=result.get('cluster'),
                    radiant_team=result.get('radiant_team'),
                    dire_team=result.get('dire_team'),
                    barracks_status_dire=result.get('barracks_status_dire'),
                    barracks_status_radiant=result.get('barracks_status_radiant'),
                    detailed=result.get('detailed'),
                    dire_score=result.get('dire_score'),
                    engine=result.get('engine'),
                    first_blood_time=result.get('first_blood_time'),
                    flags=result.get('flags'),
                    human_players=result.get('human_players'),
                    leagueid=result.get('leagueid'),
                    picks_bans=[
                        PickBanType(
                            is_pick=pb.get('is_pick'),
                            hero_id=pb.get('hero_id'),
                            team=pb.get('team'),
                            order=pb.get('order')
                        ) for pb in picks_bans if pb 
                    ],
                    players=[
                        PlayerType(
                            account_id=p.get('account_id'),
                            player_slot=p.get('player_slot'),
                            team_number=p.get('team_number'),
                            hero_id=p.get('hero_id'),
                            hero_variant=p.get('hero_variant'),
                            item_0=p.get('item_0'),
                            item_1=p.get('item_1'),
                            item_2=p.get('item_2'),
                            item_3=p.get('item_3'),
                            item_4=p.get('item_4'),
                            item_5=p.get('item_5'),
                            backpack_0=p.get('backpack_0'),
                            backpack_1=p.get('backpack_1'),
                            backpack_2=p.get('backpack_2'),
                            item_neutral=p.get('item_neutral'),
                            additional_units=[
                                AdditionalUnitType(
                                    unitname=au.get('unitname'),
                                    item_0=au.get('item_0'),
                                    item_1=au.get('item_1'),
                                    item_2=au.get('item_2'),
                                    item_3=au.get('item_3'),
                                    item_4=au.get('item_4'),
                                    item_5=au.get('item_5'),
                                    backpack_0=au.get('backpack_0'),
                                    backpack_1=au.get('backpack_1'),
                                    backpack_2=au.get('backpack_2'),
                                    item_neutral=au.get('item_neutral'),
                                ) for au in p.get('additional_units', []) if au 
                            ],
                            # stats
                            kills=p.get('kills'),
                            deaths=p.get('deaths'),
                            assists=p.get('assists'),
                            leaver_status=p.get('leaver_status'),
                            last_hits=p.get('last_hits'),
                            denies=p.get('denies'),
                            gold_per_min=p.get('gold_per_min'),
                            xp_per_min=p.get('xp_per_min'),
                            level=p.get('level'),
                            net_worth=p.get('net_worth'),
                            aghanims_scepter=p.get('aghanims_scepter'),
                            aghanims_shard=p.get('aghanims_shard'),
                            moonshard=p.get('moonshard'),
                            hero_damage=p.get('hero_damage'),
                            tower_damage=p.get('tower_damage'),
                            hero_healing=p.get('hero_healing'),
                            scaled_hero_damage=p.get('scaled_hero_damage'),
                            scaled_tower_damage=p.get('scaled_tower_damage'),
                            scaled_hero_healing=p.get('scaled_hero_healing'),
                            gold=p.get('gold'),
                            gold_spent=p.get('gold_spent'),
                            ability_upgrades=[
                                AbilityUpgradeType(
                                    ability=au.get('ability'),
                                    time=au.get('time'),
                                    level=au.get('level')
                                ) for au in p.get('ability_upgrades', []) if au  
                            ]
                        ) for p in players if p  
                    ],
                    pre_game_duration=result.get('pre_game_duration'),
                    radiant_score=result.get('radiant_score'),
                    tower_status_dire=result.get('tower_status_dire'),
                    tower_status_radiant=result.get('tower_status_radiant')
                )

            
                formattedResults.append(match_data)

            except Exception as e:
                print(f"Error processing match_id: {match_id}, error: {e}")

        return formattedResults


    all_hero_stats = graphene.List(
        HeroStatsType,
        avg_rank_tier = graphene.Int(default_value=0),
        min_played_overall=graphene.Int(default_value=0),
        min_played_radiant=graphene.Int(default_value=0),
        min_played_dire=graphene.Int(default_value=0),
        min_win_overall=graphene.Float(default_value=0),
        min_win_radiant=graphene.Float(default_value=0),
        min_win_dire=graphene.Float(default_value=0)

    )
    def resolve_all_hero_stats(self,info,avg_rank_tier=0,min_played_overall=0,min_played_radiant=0,min_played_dire=0,min_win_overall=0,min_win_radiant=0,min_win_dire=0):
        query = pipelines.getWinRatesQuery(avg_rank_tier,min_played_overall,min_played_radiant,min_played_dire,min_win_overall,min_win_radiant,min_win_dire)
        if not isinstance(query,list):
            raise ValueError("pipeline not list")
        results=list(Match.objects.aggregate(query))
        formatted_results = [   #cant really understand why this is needed? But throws unexpected values otherwise
        HeroStatsType(
            hero_id=result.get('hero_id'),
            total_games=result.get('total_games'),
            total_wins=result.get('total_wins'),
            radiant_games=result.get('radiant_games'),
            radiant_wins=result.get('radiant_wins'),
            dire_games=result.get('dire_games'),
            dire_wins=result.get('dire_wins'),
            overall_win_rate=result.get('overall_win_rate'),
            radiant_win_rate=result.get('radiant_win_rate'),
            dire_win_rate=result.get('dire_win_rate')
        )
            for result in results
         ]
        return formatted_results

        

    # Abilities
    all_abilities = graphene.List(AbilitiesType)
    abilities_by_hero_id = graphene.Field(AbilitiesType, hero_id=graphene.Int(required=True))
    abilities_by_hero_name = graphene.Field(AbilitiesType, hero_name=graphene.String(required=True))

    def resolve_all_abilities(self, info):
        return Abilities.objects.all()

    def resolve_abilities_by_hero_id(self, info, hero_id):
        '''The abilities/talents vdf used to populate the abilities page does not contain all talents --specifically when they do not affect an ability directly
            so we will pull the talents and abilities from hero too and attempt to translate them with their placeholders 
            furthermore the vdf being pulled from the client, sometimes replaced entries are not removed/flagged as removed. e.g. lina abilities dragon_slave_crits was replaced by all crit_debuff but both exist in vdf'''
        localization = current_app.config['LOCALIZATION_DATA'] #consider setting appcontext and loading this once? 
        res= Abilities.objects(hero_id=hero_id).first()  
        talents2 = Hero.objects(hero_id=hero_id).first()['talents']
        talent = res['talents']
        ability= res['abilities']
        
        for a in ability:
            ability[a]['tooltip'] = utils.map_localization_for_ability(a,localization,ability,talent)
        
        count=0
        level='10'
        
        for i in range(0,8):#talents2 has a different data structure indicating levels 
            t= talents2[level][i%2]['name'] 
            if t not in talent:
                talent[t] ={}
            
            talent[t]['tooltip']= utils.map_localization_for_talents_recur(t,localization,ability,talent)
            if(i%2==1):
                level = str(int(level)+5)
            
        return res
        


    def resolve_abilities_by_hero_name(self, info, hero_name):
        return Abilities.objects(hero_name=hero_name).first()  

    #Items
    all_items = graphene.List(ItemType)
    item_by_id = graphene.Field(ItemType,item_id=graphene.Int(required=True))
    items_by_ids = graphene.List(ItemType,item_ids = graphene.List(graphene.Int,required=True))
    def resolve_all_items(self,info):
        return Item.objects.all()

    def resolve_item_by_id(self, info, item_id):
        return Item.objects(item_id=item_id).first()

    def resolve_items_by_ids(self,info,item_ids):
        return Item.objects(item_id__in=item_ids)

class CreateHero(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        localized_name = graphene.String(required=True)

    hero = graphene.Field(lambda: HeroType)

    def mutate(self, info, name, localized_name):
        hero = Hero(name=name, localized_name=localized_name)
        hero.save()
        return CreateHero(hero=hero)

class Mutation(graphene.ObjectType):
    create_hero = CreateHero.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
