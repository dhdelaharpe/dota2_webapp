import React, {useState} from 'react';
import './TalentTree.css';
import TalentTreeimg from '../../assets/talent_tree.svg'

const TalentTree= ({talents,selectedTalents,sortedTalents})=>{ //expects hero.talents
    const [showTooltip, setShowTooltip] = useState(false);



    const handleMouseOver= (e)=>{
        setShowTooltip(true);
    };

    const handleMouseLeave=()=>{
        setShowTooltip(false);
    };

    const fillLeaves=()=>{
        const leaves={};  
        selectedTalents.forEach(talent=>{
            const {ability_id} = talent;
            Object.keys(sortedTalents).slice().reverse().forEach(level=>{
                
                const talentsAtLevel = sortedTalents[level];
                //find matching talent
            
                talentsAtLevel.forEach((talentAtLevel, index)=>{
                    if(talentAtLevel.ability_id===ability_id){
                        const levelIndex = parseInt(level/5); 
                        const position =index===0?'l':'r';
                        const leafKey = `${position}${levelIndex-1}`;
                        leaves[leafKey]=1;
                    }
                });
            });
        }); 
        return leaves;
    };

    const filledLeaves = fillLeaves();
    
    return (
        <div className='talent-tree-container'>
            <div className='talent-tree'>

                <svg className='base-tree' xmlns='http://www.w3.org/2000/svg'
                    viewBox='0 0 500 500'
                    x='0px'
                    y='0px'
                    style={{enableBackground:'new 0 0 500 500'}}
                    xmlSpace='preserve'
                    onMouseEnter={(e)=>handleMouseOver(e)}
                    onMouseLeave={handleMouseLeave}
                >
                    <g id="g5">
                        <path
                            className="st0"
                            d="M457.8,250c0,121.1-93.1,219.2-207.8,219.2S42.2,371.1,42.2,250S135.2,30.8,250,30.8S457.8,128.9,457.8,250z    M250,48.8C144.6,48.8,59.2,138.9,59.2,250S144.6,451.2,250,451.2S440.8,361.1,440.8,250S355.4,48.8,250,48.8z"
                            id="path1" />
                        <g id="g4" >
                            <g id="g3">
                                <path className={filledLeaves?.r2? 'fill':'st0'}
                                    d="m 262,302.1 c 1.5,0.7 15,-9.4 18.9,-11 3.9,-1.5 45.9,-0.2 48.3,-1.2 2.4,-1 9.3,-12.1 12.8,-16 3.5,-3.9 26.2,-16.9 37.5,-21.8 11.3,-4.9 36.1,-10.1 37.6,-8.9 1.5,1.2 -42.2,54 -54.2,56.9 -12,2.9 -71.7,2.6 -77.9,4.6 -6.2,2 -21.6,13 -22.6,15.7"
                                    id="path13" />
                                <path className={filledLeaves?.r3? 'fill':'st0'}
                                    d="m 261.9,230.3 c 3.5,0 24,-15.9 24,-15.9 0,0 32.5,0.9 33.4,-1.7 2.2,-6.4 14.8,-20.1 29.3,-31.4 19,-14.8 40.8,-26.9 41.9,-26.7 1.2,0.2 -11,26.5 -25.5,46.1 -10.4,14 -22.6,23.2 -29,23.9 -15.5,1.7 -46.7,1.2 -46.7,1.2 l -27,19.9"
                                    id="path15" />
                                <path className={filledLeaves?.r4? 'fill':'st0'}
                                    d="m 249.1,163.8 c 0,0 27.4,-13.8 27.7,-16.9 2.2,-24.5 40,-61.5 47.4,-61.4 1.3,1.2 -7.4,36 -11,44.4 -2.9,7 -10.8,22.8 -17.2,27.2 -2.9,2 -14.3,3.6 -21.4,6.1 -8,2.7 -11.6,6.3 -12.7,8.9"
                                    id="path17" />
                                <path className={filledLeaves?.r1? 'fill':'st0'}
                                    d="m 262.4,390.3 c 1.9,0.8 14.3,-10.6 20.6,-13.5 6.2,-2.9 20.2,-3.7 24,-4.7 3.7,-1 13.4,-14.2 26.3,-22.1 9.5,-5.9 46.1,-10.8 55.3,-5 3.8,2.4 -51.6,39.5 -59.2,41.2 -7.6,1.7 -37.2,-0.2 -41.9,1.5 -4.7,1.7 -22.4,15.5 -24,23.6"
                                    id="path2" />
                                <path className={filledLeaves?.l1? 'fill':'st0'}
                                    d="m 237.6,390.3 c -1.9,0.8 -14.3,-10.6 -20.6,-13.5 -6.2,-2.9 -20.2,-3.7 -24,-4.7 -3.7,-1 -13.4,-14.2 -26.3,-22.1 -9.5,-5.9 -46.1,-10.8 -55.3,-5 -3.8,2.4 51.6,39.5 59.2,41.2 7.6,1.7 37.2,-0.2 41.9,1.5 4.7,1.7 22.4,15.5 24,23.6"
                                    id="path5" />
                                <path className={filledLeaves?.l2? 'fill':'st0'}
                                    d="m 238,302.1 c -1.5,0.7 -15,-9.4 -18.9,-11 -3.9,-1.5 -45.9,-0.2 -48.3,-1.2 -2.4,-1 -9.3,-12.1 -12.8,-16 -3.5,-3.9 -26.2,-16.9 -37.5,-21.8 -11.3,-4.9 -36.1,-10.1 -37.6,-8.9 -1.5,1.2 42.2,54 54.2,56.9 12,2.9 71.7,2.6 77.9,4.6 6.2,2 21.6,13 22.6,15.7"
                                    id="path6" />
                                <path
                                    id="path9"
                                    className={Object.keys(filledLeaves).length>0?"fill":"base"}
                                    d="m 237.8,311.25 c -0.84108,10.79204 0.54553,56.01862 -0.53089,78.70993 -0.24599,5.18558 -0.29068,8.50952 -0.74642,10.63012 0.19184,3.75606 -0.10792,8.35728 -0.0834,13.0797 0.097,18.66297 0.0607,41.53025 0.0607,41.53025 l 13.73474,0.0716 -0.27173,-290.91446 -5.9428,2.76413 c -0.8146,0.76406 -5.52213,1.73714 -5.7949,4.89737 -0.32843,3.80515 0.2982,8.67214 0.12609,13.70204 -0.18074,5.28198 -0.14995,19.88846 -0.20899,25.84008 -0.15495,15.6183 0.19506,22.63919 -0.2424,26.43924 0,0 0.4747,62.93868 -0.1,73.25 z M 261.9,172.1 c -2,5.1 -0.0798,58.66627 0.2,65.9 0,0 0.33343,2.9465 0.22095,7.79731 -0.39531,17.0488 -1.56655,55.75774 -0.32095,56.30269 -0.12809,4.48313 0.42927,11.17208 0.30935,18.8094 -0.34508,21.97641 -0.3813,52.97657 0.29463,69.73242 0.1895,4.6976 0.46846,8.10188 0.89038,10.0652 -0.15665,3.06711 -0.057,6.51194 -0.0981,10.27679 C 263.18797,430.05032 263.5,455.2 263.5,455.2 l -13.25779,0.0782 -0.23938,-290.85774 -0.0812,-0.12326"
                                        />
                                <path className={filledLeaves?.l3? 'fill':'st0'}
                                    d="m 238.1,230.3 c -3.5,0 -24,-15.9 -24,-15.9 0,0 -32.5,0.9 -33.4,-1.7 -2.2,-6.4 -14.8,-20.1 -29.3,-31.4 -19,-14.8 -40.8,-26.9 -41.9,-26.7 -1.2,0.2 11,26.5 25.5,46.1 10.4,14 22.6,23.2 29,23.9 15.5,1.7 46.7,1.2 46.7,1.2 l 27,19.9"
                                    id="path8" />
                                <path className= {filledLeaves?.l4? 'fill':'st0'}
                                    d="m 250.9,163.8 c 0,0 -27.4,-13.8 -27.7,-16.9 -2.2,-24.5 -40,-61.5 -47.4,-61.4 -1.3,1.2 7.4,36 11,44.4 2.9,7 10.8,22.8 17.2,27.2 2.9,2 14.3,3.6 21.4,6.1 8,2.7 11.6,6.3 12.7,8.9"
                                    id="path10" />
                            </g>
                        </g>
                    </g>
                </svg>
                
                {showTooltip &&(
                    <div className='tooltip'>
                        {Object.keys(sortedTalents).slice().reverse().map(level=>{
                            return(
                                <div key={level} className='talent-level'>
                                    <div className={filledLeaves[`l${level/5-1}`]? 'selected-talent':''}>
                                       <h6> {talents?.[sortedTalents?.[level]?.[0].name]?.tooltip?.name ?? sortedTalents?.[level]?.[0].name}</h6>
                                    </div>

                                    <div>{level}</div>
                                    <div className={filledLeaves[`r${level/5-1}`]?'selected-talent':''}>
                                       <h6> {talents?.[sortedTalents?.[level]?.[1].name]?.tooltip?.name ?? sortedTalents?.[level]?.[1].name}</h6>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
                
            </div>
        </div>
    )
};
export default TalentTree;