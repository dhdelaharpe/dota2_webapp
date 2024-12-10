    import React, { useEffect, useState, useCallback , useRef} from 'react';
    import { useParams } from 'react-router-dom';
    import { useNavigate } from 'react-router-dom';

    import { fetchHeroes } from './HeroOverview'; // consider moving to a utils file
    import { columnOptions } from './HeroOverviewFilter';
    import { useHeroes } from './HeroesContext';
    import RecentHeroMatches from './RecentHeroMatches'
    import TalentTree from './TalentTree';
    import Tooltip from './Tooltip';
    import './HeroInfo.css';
    //import { template } from '@babel/core';

    // Utility Functions
    const capitalizeFirstLetter = (str) => str.charAt(0).toUpperCase() + str.slice(1);
    const truncateAtSentence=(text,maxLength)=>{
        if (text.length<maxLength) return text;

        //support end of sentence with . ! ? 
        const truncatedText = text.slice(0,maxLength);
        const lastSentenceEnd= Math.max( //consider using an array for ending punctuation? 
            truncatedText.lastIndexOf('.'),
            truncatedText.lastIndexOf('?'),
            truncatedText.lastIndexOf('!')
        );
        return lastSentenceEnd===-1? truncatedText: truncatedText.slice(0,lastSentenceEnd+1);
    };
    const getGradient = (color, gradientId) => {
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
      
    const HeroInfo = () => {
        const navigate = useNavigate();
        const { heroes, setHeroes } = useHeroes();
        const { heroId } = useParams();
        const [hero, setHero] = useState(null);
        const [abilities, setAbilities] = useState(null);
        const [talents, setTalents] = useState(null);
        const [sortedAbilities, setSortedAbilities] = useState(null);
        const [descIsExpanded, setDescIsExpanded] = useState(false); 
        const [loading, setLoading]= useState(true);
        const [validIds,setValidIds] = useState(null);
        
        const usedAbilitiesRef = useRef(new Set());

        // Navigate on click
        const handleOnClick = useCallback((heroId,direction) => {
            if(validIds.includes(heroId)){
                navigate(`/hero/${heroId}`);  
            }else if(direction===-1){
                navigate(`/hero/${validIds[validIds.length-1]}`);
            }else if(direction===1){
                navigate(`/hero/${validIds[0]}`);
            }   
        },[navigate, validIds])

        const handleKeyDown =useCallback((event)=>{ 
            if(validIds && loading===false){
                const {key} = event;
                if (key==='ArrowLeft'){
                    handleOnClick(validIds[validIds.indexOf(parseInt(heroId))-1],-1);
                }else if(key==='ArrowRight'){
                    handleOnClick(validIds[validIds.indexOf(parseInt(heroId))+1],1);
            }
            }
        },[handleOnClick, heroId, loading, validIds])


        //expand description/lore
        const handleToggleDescription= ()=>{
            setDescIsExpanded(!descIsExpanded);
        }
        // Fetch abilities only when heroId changes
        const fetchAbilities = useCallback(async (heroId) => {
            const response = await fetch('/api/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                query: `
                    query($heroId:Int!) {
                    abilitiesByHeroId(heroId: $heroId) {
                        abilities
                        talents
                    }
                    }`,
                variables: { heroId: parseInt(heroId, 10) }
                })
            });
            const dataRes = await response.json();
            return dataRes.data.abilitiesByHeroId;

        }, []);

        // Sort abilities based on their type
        const sortAbilities = useCallback((abilities,talents, templateAbilities) => {
            const usedAbilities = usedAbilitiesRef.current;
            const sortedAbilities = [];
            
            templateAbilities.forEach(ta=> { 
            
            const tAbility=JSON.parse(ta.replace(/'/g, '"')); //very strangely it is appearing with single quotes and breaking parse  
                if (tAbility.name === 'generic_hidden') {
                    const availableName = Object.keys(abilities).find(abilName => 
                        !usedAbilities.has(abilName)
                    );
                    if (availableName) {
                        usedAbilities.add(availableName); // Mark as used
                        
                        const abilityData = abilities[availableName];
                        const behaviors = Array.isArray(abilityData.AbilityBehavior)
                            ? abilityData.AbilityBehavior
                            : [abilityData.AbilityBehavior];
                        
                        if (behaviors.some(behavior => behavior === 'DOTA_ABILITY_BEHAVIOR_INNATE_UI') || abilityData.Innate === "1") {
                            sortedAbilities.push({ innate: { ...abilityData, name: availableName } });
                        }
                        else if(behaviors.some(behavior=> behavior==='Hidden')){
                            sortedAbilities.push({hidden: {...abilityData,name:availableName}}); 
                        }
                        
                        else {
                            sortedAbilities.push({ ...abilityData, name: availableName });
                        }
                    } else {
                        console.warn('No available name for generic_hidden');
                        sortedAbilities.push(null); 
                    }
                } else {
                    // Non-edge cases
                    if (!usedAbilities.has(tAbility.name)) { 
                        usedAbilities.add(tAbility.name); 
                        
                        const abilityData = abilities[tAbility.name];
                        const behaviors = Array.isArray(abilityData.AbilityBehavior)
                            ? abilityData.AbilityBehavior
                            : [abilityData.AbilityBehavior];
                        //ordering of behaviors is important 
                        if (behaviors.some(behavior => behavior === 'DOTA_ABILITY_BEHAVIOR_INNATE_UI') || abilityData.Innate === "1") {
                            sortedAbilities.push({ innate: { ...abilityData, name: tAbility.name } });
                        } 
                        else if(behaviors.some(behavior=> behavior==='Hidden')){
                            sortedAbilities.push({hidden: {...abilityData,name:tAbility.name}}); 
                        }else {
                            sortedAbilities.push({ ...abilityData, name: tAbility.name });
                        }
                    } else {
                        //console.warn(`Ability ${name} has already been used.`);
                    }
                }
            });
        
            return sortedAbilities;
        }, []);
        useEffect(()=>{
            window.addEventListener('keydown', handleKeyDown);

            return ()=>{
                window.removeEventListener('keydown',handleKeyDown);
            };
        },[handleKeyDown])

        useEffect(()=>{//separating useEffects to avoid fetching everything unnecessarily 
        if(!heroes.length){
            const fetchAllHeroes=async()=>{
                const data = await fetchHeroes();
                setHeroes(data);
            };
            fetchAllHeroes();
        }
        
        },[heroes.length,setHeroes]);

        useEffect(()=>{
            
            const fetchData= async()=>{
                if(heroId&&heroes.length){
                    setLoading(true);
                    const heroData =heroes.find(h=>h.heroId===parseInt(heroId,10));
                    setHero(heroData);
                    setAbilities(null);
                    const abilAndTalents= await fetchAbilities(heroId);
                    setAbilities(JSON.parse(abilAndTalents.abilities));//raw unsorted
                    setTalents(JSON.parse(abilAndTalents.talents)); //raw unsorted      
                    setValidIds(heroes.map(hero=> hero.heroId));
                    setLoading(false);
                }
            };
            fetchData();
        },[heroId,heroes,fetchAbilities]);

        useEffect(()=>{
            const sortAbilTalentsData=()=>{
                if(abilities){
                    setLoading(true);
                    usedAbilitiesRef.current.clear();
                    setSortedAbilities(null);
                    const sorted= sortAbilities(abilities, talents, hero?.abilities); // TODO change this logic to something more sensible
                    setSortedAbilities(sorted);
                    setLoading(false);
                }
            }
            sortAbilTalentsData();
            
        },[abilities, hero?.abilities,hero?.talents, sortAbilities, talents])
        if(loading){
            return <div>Loading...</div>
        }
        if (!hero || !sortedAbilities) {
            
        return <div>Hero not found ...???</div>;
        }
        
        const facets = JSON.parse(hero.facets);
        
        return ( // Could easily separate these into multiple components since they have grown quite large. 
        <div className='hero-info'>
            <div className='hero-header'>
            <div className='hero-animated'>
                <video src={hero.animated} autoPlay loop muted playsInline />
                <div className='hero-name'>
                    <p className='selector'style={{width:'15%',cursor:'pointer'}}onClick={()=>handleOnClick(validIds[validIds.indexOf(parseInt(heroId))-1],-1)}>Previous</p>
                    <h1 style={{width:'60%'}}>{hero.localizedName}</h1>
                    <p className='selector'style={{width:'15%',cursor:'pointer'}} onClick={()=>handleOnClick(validIds[validIds.indexOf(parseInt(heroId))+1],1)}>Next</p>
                </div>
                <div className='hero-description'>
                    <p>
                        {descIsExpanded? hero.description: `${truncateAtSentence(hero.description,200)} ...`}
                    </p>
                    <button onClick={handleToggleDescription}>
                        {descIsExpanded? 'hide': 'Read full lore'}
                    </button>
                </div>
                <div className='attribute-container'>
                    <img src={hero.attribute ? columnOptions.find(opt => opt.value === hero.attribute).icon : ''} alt='' />
                    <h2>{capitalizeFirstLetter(hero.attribute.toLowerCase())}</h2>
                </div>

                <div className='role-containers'>
                <h3>Roles</h3>
                {hero.roles.map((role, index) => (
                    <div className='role' key={role}>
                        <div className='role-name-info'style={{fontSize:"1.2em"}}>{role}</div>
                        <div className='role-bar' style={{ width: `${50*((hero.roleLevels[index]) / 3).toFixed(2)}%` }} />
                    </div>
                ))}
                </div>

                <div className='similar-heroes'>
                    <h3>Similar heroes</h3>
                {hero.similar.map(hId => {
                    const sim = heroes.find(h => hId === h.heroId);
                    return (
                    <div key={hId} className='similar-hero'onClick={() => handleOnClick(hId)}>
                        {sim.localizedName}
                    </div>
                    );
                })}
                </div>
            </div>
            </div>
            <div className='facet-container'>
                <div className='facets-header'><h2>Facets</h2></div>
                <div className='facets-body'>
                    {
                    Object.keys(facets).map(facet=>{
                        return(
                        <Tooltip key={facet} content={facets[facet].tooltip.description}>
                        <div key={facet} className='facet' style={{
                            display:'flex',
                            backgroundImage:`${getGradient(facets[facet].Color,facets[facet].GradientID)},url('https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/facets/ripple_texture.png')`,
                            textShadow:' 0px 2px 8px rgba(0, 0, 0, .5)',
                            backgroundSize:'cover,cover',
                            backgroundBlendMode:'hard-light',
                            color:'#fff',
                            opacity:'0.9',
                            alignItems:'center',
                            maxWidth:'18rem',
                            padding:'0.2rem',
                            
                        }}>
                            
                            <img src={facets[facet].Icon} alt={facet} />
                            <h3>{facets[facet].tooltip.name}</h3>
                            
                        </div>
                        </Tooltip>
                    )})}
                </div>
            </div>
            
            <TalentTree talents={talents} selectedTalents={[false,false,false,false]} sortedTalents={JSON.parse(hero.talents)}/>
            
            <div className='abilities-container'>
                <div className='abilities-header'><h2>Abilities</h2></div>
                <div className='abilities-body'>
                    <Tooltip content={sortedAbilities.find(ability=>Object.prototype.hasOwnProperty.call(ability,'innate')).innate.tooltip.description}>
                        <div className='innate'>
                         <img src={`https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/icons/innate_icon.png`} alt={sortedAbilities.find(ability=>Object.prototype.hasOwnProperty.call(ability,'innate')).innate.tooltip.name} />
                        </div>
                    </Tooltip>
                    {sortedAbilities.map(ability => {
                        if(ability===null ){
                            return null;
                        }
                        
                        if(!(ability.innate|| ability.hidden)&& !ability.name.startsWith('invoker_empty' )){
                            return(
                                <Tooltip key={ability.name} content={ability.tooltip.description} ability={ability}>
                                    <div className={Object.prototype.hasOwnProperty.call(ability,'IsGrantedByShard')?'shard-ability':'ability'}>
                                    <img src={ability.img} alt={ability.name} />
                                    </div>
                                </Tooltip>
                            );
                        }
                        return null;
                    })}

                </div>
            </div>
            <RecentHeroMatches key={heroId} heroId={heroId} limit={10} avgRankTier={8} talents={talents} abilities={abilities}/>
        </div>
        );
    };

    export default HeroInfo;
