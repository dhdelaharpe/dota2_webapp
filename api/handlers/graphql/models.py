from mongoengine import Document, EmbeddedDocument, DynamicDocument, CASCADE
from mongoengine.fields import DateTimeField, ListField, ReferenceField, StringField, IntField, URLField,DictField, BooleanField, EmbeddedDocumentListField, LongField, FloatField, EmbeddedDocumentField

class Hero(DynamicDocument): #not sure if all heroes have the same fields and we're dumping the json direclty into db so use dynamic
    meta= {"collection":"heroes_live"}
    hero_id=IntField(required=True,unique=True)
    name=StringField(required=True)
    localized_name = StringField(required=True)
    img_full = URLField(required=True)
    img_small = URLField(required=True)
    animated = URLField()
    aliases = ListField(StringField(),default=[])
    roles = ListField(StringField(),default=[])
    role_levels = ListField(IntField(), default=[])
    similar = ListField(IntField(),default=[])
    abilities = ListField(StringField(),default=[])     #these are repeated here with just their names, avoids having the fetch from abilities and link to hero every time when just the names of abilities are required
    talents = DictField(ListField(DictField()),default={})
    facets=DictField()
    attribute=StringField()
    description=StringField()


class HeroStats(Document):
    hero_id = IntField()
    total_games = IntField()
    total_wins = IntField()
    radiant_games = IntField()
    radiant_wins = IntField()
    dire_games = IntField()
    dire_wins = IntField()
    overall_win_rate = FloatField()
    radiant_win_rate = FloatField()
    dire_win_rate = FloatField()

class HeroPickBanRate(Document):
    hero_id = IntField()
    contested = IntField()
    total_games = IntField()
    contest_rate = FloatField()

class Abilities(DynamicDocument):#using dynamic here as the amount of entries varies between heroes. Plural because an entry represents all abilities from 1 hero
    meta= {"collection":"abilities"}
    hero_id= IntField(required=True) 
    hero_name = StringField(required=True)
    abilities = DictField(required=True)
    talents = DictField(required=True)

class PickBan(EmbeddedDocument):
    is_pick = BooleanField(required=True)
    hero_id = IntField(required=True)
    team = IntField(required=True)
    order = IntField(required=True) 

class AbilityUpgrade(EmbeddedDocument):
    ability = IntField(required=True) #noticed an issue here as abilityID does not appear in the abilities data yet? 
    time = IntField(required=True)
    level = IntField(required=True)

class AdditionalUnit(EmbeddedDocument):
    unitname = StringField(required=True)
    item_0 = IntField()
    item_1 = IntField()
    item_2 = IntField() 
    item_3 = IntField() 
    item_4 = IntField() 
    item_5 = IntField()
    backpack_0 = IntField() 
    backpack_1 = IntField() 
    backpack_2 = IntField() 
    item_neutral = IntField() 

class Player(EmbeddedDocument):
    account_id = LongField(required=True) 
    player_slot = IntField(required=True)
    team_number= IntField(required=True)
    team_slot = IntField(required=True)
    hero_id = IntField(required=True)
    hero_variant = IntField(required=True) # facet 
    #itemization
    item_0 = IntField()
    item_1 = IntField()
    item_2 = IntField() 
    item_3 = IntField() 
    item_4 = IntField() 
    item_5 = IntField()
    backpack_0 = IntField() 
    backpack_1 = IntField() 
    backpack_2 = IntField() 
    item_neutral = IntField() 
    #in case of additional units e.g. lone druid
    additional_units = EmbeddedDocumentListField(AdditionalUnit)
    #stats
    kills = IntField()
    deaths =IntField() 
    assists = IntField() 
    leaver_status = IntField() 
    last_hits = IntField() 
    denies = IntField() 
    gold_per_min = IntField()
    xp_per_min = IntField()
    level = IntField(required=True)
    net_worth = IntField(required=True)
    aghanims_scepter = BooleanField()   
    aghanims_shard = BooleanField()
    moonshard = BooleanField()
    #throughput
    hero_damage = IntField()
    tower_damage = IntField()
    hero_healing = IntField()
    scaled_hero_damage = IntField()
    scaled_tower_damage = IntField()
    scaled_hero_healing = IntField()

    gold = IntField() 
    gold_spent = IntField()
    
    ability_upgrades = EmbeddedDocumentListField(AbilityUpgrade)


class Match(Document):
    meta={"collection":"matches"}
    match_id = IntField(required=True,unique=True)
    match_seq_num = IntField(required=True)
    radiant_win = BooleanField(required=True)
    start_time = StringField()#DateTimeField(required=True)
    duration = IntField(required=True)
    lobby_type = IntField(required=True,choices=(1,2,3,4,5,6,7,8))
    game_mode = IntField(required=True,choices=(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23))
    avg_rank_tier = IntField(required=True)
    num_rank_tier = IntField(required=True)
    cluster = IntField(required=True)
    radiant_team = ListField(IntField(), required = True)
    dire_team = ListField(IntField(), required=True)
    barracks_status_dire = IntField()
    barracks_status_radiant= IntField()
    detailed = BooleanField()
    dire_score= IntField()
    engine= IntField()
    first_blood_time = IntField() #seconds from start? 
    flags= IntField()
    human_players = IntField()
    leagueid = IntField()
    picks_bans = EmbeddedDocumentListField(PickBan)
    players = EmbeddedDocumentListField(Player)
    pre_game_duration = IntField()
    radiant_score = IntField()
    tower_status_dire = IntField()
    tower_status_radiant = IntField()
    
class Ability(EmbeddedDocument):
    type = StringField(required=True)
    title = StringField(required=True)
    description = StringField(required=True)


class Attribute(EmbeddedDocument):
    key = StringField(required=True)
    display = StringField()  
    value = StringField(required=True)  
    header = StringField(default='')
    footer = StringField(default='')
    generated = StringField(default='')

class Item(Document):
    meta = {"collection": "items"}
    item_id = IntField(required=True)
    img = StringField()
    dname = StringField()
    qual = StringField()
    cost = IntField()
    behavior = StringField()
    dmg_type = StringField()
    notes = StringField()
    cd = FloatField()  
    lore = StringField()
    mc = BooleanField() 
    hc = BooleanField() 
    created = BooleanField() 
    charges = BooleanField() 
    abilities = ListField(EmbeddedDocumentField(Ability),default=[])
    attrib = ListField(EmbeddedDocumentField(Attribute),default=[]) 
    components = ListField(StringField(),default=[])
    hint = ListField(StringField(), default=[])
    target_type = StringField(default='')
    target_team = StringField(default='')
    dispellable = StringField(default='')
    bkbpierce = StringField(default='')
    desc = StringField(default='')
    tier =IntField(default=0)





