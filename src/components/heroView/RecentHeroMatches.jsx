import React, {useCallback,useEffect,useState} from 'react';
import './RecentHeroMatches.css';
import {useHeroes} from './HeroesContext';
import TalentTree from './TalentTree';
import talentTreeEmpty from  '../../assets/images/empty_sm_nobg.webp';
import attribute_bonus from '../../assets/images/attribute_bonus.webp';
const calcDaysAgo=(starttime)=>{
    const now = new Date();
    const matchDate = new Date(starttime);
    const td = now-matchDate;
    const daysAgo = Math.floor(td/(1000*60*60*24));
    return daysAgo
};
const getGradient = (color, gradientId) => { //TODO: move to a utils file
    const gradients = {
      purple: [
        "linear-gradient(to right, rgb(156, 112, 164), rgb(40, 39, 82))", // GradientID 0
        "linear-gradient(to right, rgb(130, 80, 150), rgb(90, 45, 120))", // GradientID 1
        "linear-gradient(to right, rgb(180, 130, 200), rgb(110, 60, 150))", // GradientID 2
        "linear-gradient(to right, rgb(150, 100, 170), rgb(120, 80, 160))", // GradientID 3
        "linear-gradient(to right, rgb(130, 90, 160), rgb(50, 30, 100))",  // GradientID 4
      ],
      blue: [
        "linear-gradient(to right, rgb(148, 181, 186), rgb(56, 91, 89))", // GradientID 0
        "linear-gradient(to right, rgb(100, 140, 180), rgb(50, 85, 120))", // GradientID 1
        "linear-gradient(to right, rgb(160, 190, 200), rgb(80, 130, 170))", // GradientID 2
        "linear-gradient(to right, rgb(120, 160, 180), rgb(90, 140, 160))", // GradientID 3
        "linear-gradient(to right, rgb(100, 140, 160), rgb(40, 70, 90))",  // GradientID 4
      ],
      red: [
        "linear-gradient(to right, rgb(255, 77, 77), rgb(136, 8, 8))", // GradientID 0
        "linear-gradient(to right, rgb(230, 66, 66), rgb(120, 10, 10))", // GradientID 1
        "linear-gradient(to right, rgb(255, 102, 102), rgb(170, 20, 20))", // GradientID 2
        "linear-gradient(to right, rgb(240, 50, 50), rgb(160, 30, 30))",  // GradientID 3
        "linear-gradient(to right, rgb(210, 40, 40), rgb(130, 20, 20))",  // GradientID 4
      ],
      green: [
        "linear-gradient(to right, rgb(105, 200, 85), rgb(40, 80, 30))", // GradientID 0
        "linear-gradient(to right, rgb(80, 160, 65), rgb(30, 65, 20))",  // GradientID 1
        "linear-gradient(to right, rgb(125, 220, 100), rgb(50, 100, 50))", // GradientID 2
        "linear-gradient(to right, rgb(100, 180, 80), rgb(40, 80, 40))",  // GradientID 3
        "linear-gradient(to right, rgb(90, 150, 70), rgb(35, 70, 35))",  // GradientID 4
      ],
      yellow: [
        "linear-gradient(to right, rgb(255, 240, 128), rgb(200, 180, 30))", // GradientID 0
        "linear-gradient(to right, rgb(240, 220, 110), rgb(180, 160, 40))", // GradientID 1
        "linear-gradient(to right, rgb(255, 230, 140), rgb(220, 190, 50))", // GradientID 2
        "linear-gradient(to right, rgb(245, 215, 100), rgb(200, 170, 45))", // GradientID 3
        "linear-gradient(to right, rgb(230, 200, 90), rgb(170, 150, 40))",  // GradientID 4
      ],
      grey: [
        "linear-gradient(to right, rgb(170, 170, 170), rgb(100, 100, 100))", // GradientID 0
        "linear-gradient(to right, rgb(140, 140, 140), rgb(90, 90, 90))",  // GradientID 1
        "linear-gradient(to right, rgb(190, 190, 190), rgb(120, 120, 120))", // GradientID 2
        "linear-gradient(to right, rgb(160, 160, 160), rgb(110, 110, 110))", // GradientID 3
        "linear-gradient(to right, rgb(120, 120, 120), rgb(80, 80, 80))",   // GradientID 4
      ]
    };
  
    const colorKey = color.toLowerCase();
    return gradients[colorKey] && gradients[colorKey][gradientId]
      ? gradients[colorKey][gradientId]
      : gradients.grey[0]; // Fallback to grey gradient
  };
const RecentHeroMatches=({heroId,limit,avgRankTier, talents,abilities})=>{
    const [matches,setMatches] = useState(null);
    const [items,setItems] = useState(null);
    const {heroes, _} = useHeroes();
    


    const fetchItems = useCallback(async (itemIds)=>{
        const response = await fetch('/api/graphql',{
            method:"POST",
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                query:`
                    query($itemIds:[Int!]!){
                        itemsByIds(itemIds:$itemIds){
                            dname
                            img
                            itemId
                            cost
                        }
                    }`,
                variables:{itemIds}
            })
        });
        const dataRes = await response.json();
        return dataRes.data.itemsByIds;
    },[]);
    const fetchMatches = useCallback(async (heroId) => {
        const response = await fetch('/api/graphql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
            query: `
                query ($avgRankTier:Int!, $limit:Int!, $heroId:Int!){
                    matchEloSample(avgRankTier:$avgRankTier, limit:$limit, heroId:$heroId) {
                        matchId
                        matchSeqNum
                        radiantWin
                        startTime
                        duration
                        lobbyType
                        gameMode
                        avgRankTier
                        numRankTier
                        cluster
                        radiantTeam
                        direTeam
                        barracksStatusDire
                        barracksStatusRadiant
                        direScore
                        radiantScore 
                        firstBloodTime
                        flags
                        humanPlayers
                        leagueid
                        picksBans {
                        isPick
                        heroId
                        team
                        order
                        }
                        players{
                        accountId
                        playerSlot
                        teamNumber
                        heroId
                        heroVariant
                        item0
                        item1
                        item2
                        item3
                        item4
                        item5
                        backpack0
                        backpack1
                        backpack2
                        itemNeutral
                        additionalUnits{
                            unitname
                            item0
                            item1
                            item2
                            item3
                            item4
                            item5
                            backpack0
                            backpack1
                            backpack2
                            itemNeutral
                        }
                        kills
                        deaths
                        assists
                        leaverStatus
                        lastHits
                        denies
                        goldPerMin
                        xpPerMin
                        level
                        netWorth
                        aghanimsScepter
                        aghanimsShard
                        moonshard
                        heroDamage
                        towerDamage
                        heroHealing
                        gold
                        goldSpent
                        abilityUpgrades{
                            ability
                            time
                            level
                        }
                        }
                        preGameDuration
                        towerStatusDire
                        towerStatusRadiant
                    }
                }
                `,
            variables: { heroId: parseInt(heroId, 10),limit:parseInt(limit), avgRankTier:parseInt(avgRankTier )}
            })
        });
        const dataRes = await response.json();
        return dataRes.data.matchEloSample;
    }, [avgRankTier,limit]);

    useEffect(()=>{
        const itemIds= new Set(); //store ids 
        const getMatches= async()=>{
            
            const data= await fetchMatches(heroId); 
            
            setMatches(data);
            if(data){
            data.forEach(match=>{
                const player = match.players.find(player=>player.heroId ===parseInt(heroId));
                if(player){
                    Object.keys(player)
                    .filter(key=>key.startsWith('item')|| key.startsWith('backpack'))
                    .forEach(item=>{
                        const itemId = player[item];
                        if(itemId) itemIds.add(itemId);
                    });
                }
                if(player.additionalUnits[0]){
                    Object.keys(player.additionalUnits[0])
                    .filter(key=>key.startsWith('item'))
                    .forEach(item=>{
                        const itemId = player.additionalUnits[0][item];
                        if(itemId) itemIds.add(itemId);
                    });
                }
            });
            const itemIdsArr = Array.from(itemIds);

            // now fetch the items needed 
            if(itemIdsArr.length>0){
                fetchItems(itemIdsArr).then(items=>setItems(items));
            }
        }
        };
        getMatches();

    },[avgRankTier, fetchItems, fetchMatches, heroId, limit]);

    //map items to images for easy use
    const itemMap = {};
    if(items){
        items.forEach(item=>{//not really needed 
            itemMap[item.itemId]= item.img;
        });
    }

    //map ability upgrades -> also makes selected talents easier to access
    const mapAbilityUpgrades = (aus)=>{
        const newTalentMap=[];
        const abilityUpgrades= aus.map(au=>{
            const abilityId = au.ability;
            
            const matchedAbility= Object.values(abilities).find(ability=> ability.ability_id===abilityId);
            
            if(matchedAbility){
                return matchedAbility;
            }
            const matchedTalent = Object.values(talents).find(talent=> talent?.ability_id===abilityId);
            if(matchedTalent){
                newTalentMap.push(matchedTalent);
                return matchedTalent;
            }
            if(abilityId===5002|| abilityId===730){
                return {img:attribute_bonus, tooltip:{name:'attribute'}}
            }
            return {};
            
        })
        return {abilityUpgrades, newTalentMap};
        
    }

    if(!matches && !items){
        
        return <div>...loading matches...?</div>
    }
    
    return (
        <div className='hero-matches-container'>
            <h2>Recent Matches</h2>
            {matches.map((match,index) => {
                const player = match.players.find(player=>player.heroId===parseInt(heroId));
                const hero=heroes.find(h => h.heroId === parseInt(player.heroId))
                const isRadiant = player.teamNumber===0;
                const outcome = match.radiantWin===isRadiant? true:false;
                const matchDuration = (match.duration/60).toFixed(2).split('.')
                const daysAgo = calcDaysAgo(match.startTime);
                
                const maps = mapAbilityUpgrades(player.abilityUpgrades)
                const mappedUpgrades=maps.abilityUpgrades
                const talentMap = maps.newTalentMap
                const facetKey = Object.keys(JSON.parse(hero.facets))[player.heroVariant-1]
                const facet = JSON.parse(hero.facets)[facetKey]
                console.log(player)
                return(    
                    <div key={index} className={outcome?'hero-match-win':'hero-match-loss'}>

                        <div className='hero-match-meta'>
                            <p>Player ID: {player.accountId}</p>
                            <div className='win-loss'><h3>   {outcome?'Win ':'Loss'}</h3></div>
                            <p>Match Duration: {matchDuration[0]+':'+matchDuration[1]}</p>
                            
                            <div> <p>{daysAgo===0?"Today":daysAgo===1?daysAgo+" day ago":daysAgo+" days ago"}</p></div>
                        </div>
                        
                        <div className='hero-match-row-one'>
                        <div className='hero-match-outcome'>
                            
                            <p> Level: {player.level}</p>
                            <div className='kda'>{player.kills}/{player.deaths}/{player.assists}</div>
                            <div className='hero-match-net-worth'>{player.netWorth}</div>
                        </div>
                        <div className='hero-match-talents'>
                            <TalentTree talents={talents} selectedTalents={talentMap} sortedTalents={JSON.parse(hero.talents)}/>
                        </div>
                        <div className='draft-container'> 
                            {match.players.map((player,index)=> {
                                return(
                                    <div key={index}className={player.heroId===parseInt(heroId)?'draft-focus-hero':'draft-hero'}>
                                    <img key={index} src={heroes.find(h => h.heroId === parseInt(player.heroId))?.imgSmall} alt="" />
                                    </div>
                                )
                            })}
                        </div>
                        
                        
                        <div className='hero-throughput'>
                            <div>
                                <h4>Damage</h4>
                                {player.heroDamage}
                            </div>
                            <div>
                                <h4>Healing</h4>
                                {player.heroHealing}
                            </div>
                            <div>
                                <h4>Building Damage</h4>
                                {player.towerDamage}
                            </div>
                        </div>
                        
                        <div className='hero-items-control'>
                        <div className='hero-items-container'>
                            
                            {Object.keys(player).filter(key=>key.startsWith('item') ).map((item,index)=>{
                                const itemId = player[item];
                                const itemImg = itemMap[itemId];
                                console.log(itemMap)
                                return(
                                    <div key={`${item}-${index}`} className={(item.startsWith('item')&& item!=='itemNeutral')?'hero-item': item==='itemNeutral'?'hero-neutral-item':'hero-backpack-item'}> 
                                        {itemImg?(<img src={itemImg} alt={itemId}/>):(<span>XXX</span>)
                                        }
                                    </div>
                                )
                            })}
                            </div>
                            <div className='hero-bear-items-container'>
                            {player.additionalUnits[0]? Object.keys(player.additionalUnits[0]).filter(key=>key.startsWith('item') && key!=='itemNeutral').map((item,index)=>{
                                
                                const itemId = player.additionalUnits[0][item]
                                //console.log(itemId)
                                const itemImg = itemMap[itemId]
                                //console.log(itemImg)
                                //console.log(itemMap)
                                return(
                                    <div key={`${item}-${index}`} className={'hero-item'}> 
                                        {itemImg?(<img src={itemImg} alt={itemId}/>):(<span>XXX</span>)
                                        }
                                    </div>
                                )
                            }):''}
                            </div>
                        
                        </div>
                        
                        
                        </div>
                        <div className='hero-match-row-two'>
                        
                        <div className='hero-match-facet' style={{
                                display:'flex',
                                backgroundImage:`${getGradient(facet.Color,facet.GradientID)},url('https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/facets/ripple_texture.png')`,
                                textShadow:' 0px 2px 8px rgba(0, 0, 0, .5)',
                                backgroundSize:'cover,cover',
                                backgroundBlendMode:'hard-light',
                                color:'#fff',
                                opacity:'0.9',
                                alignItems:'center',
                                maxWidth:'18rem',
                                padding:'0.2rem',
                            }}>
                                <img src={facet.Icon} title={'facet'}/>
                                <h3>{facet.tooltip.name}</h3>
                            </div>
                            <div className='hero-match-upgrades'> 
                                
                                {Object.keys(mappedUpgrades).map(upgrade=>{
                                    return (
                                        <div key={upgrade}>
                                            <img src={mappedUpgrades[upgrade]?.img?mappedUpgrades[upgrade].img:talentTreeEmpty} title={mappedUpgrades[upgrade].tooltip? mappedUpgrades[upgrade].tooltip.name: ''}/>
                                        </div>
                                    )
                                })}
                            </div>
                        
                    </div>
                    </div>
                );
            })}
        </div>
    );
    
};


export default RecentHeroMatches;