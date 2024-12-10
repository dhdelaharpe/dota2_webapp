import  {useState, useEffect} from 'react';
import './tables.css';
import './HeroFilter.css';
import HeroTableFilter, {columnOptions} from './HeroTableFilter';
import HeroTable from './HeroTable';

//custom hook to handle fetching data 
const useFetchData =(filterValue)=>{
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [totalGames, setTotalGames] = useState(0);
    
    useEffect(()=>{
        const fetchData=async()=>{
            try{
                //populate all heroes
                
                const heroListResponse= await fetch('/api/graphql',{
                    method:'POST',
                    headers:{
                        'Content-Type':'application/json',
                    },
                    body: JSON.stringify({
                        query:`
                        {
                            allHeroes{
                              heroId
                              imgSmall
                              localizedName
                            }
                          }`
                    })
                });
                const heroesRes = await heroListResponse.json();
                const heroes = heroesRes.data.allHeroes;
                
                //get total matches
                const countResponse = await fetch(`api/matches_count?avg_rank_tier=${filterValue.avg_rank_tier}`);
                const countData = await countResponse.json();
                setTotalGames(countData.count);

                // we also need contest rate, so total games banned or picked -- removed this from aggr query as its easier to just pull if fields are indexed in db 
                const contestRateRes =  await fetch('/api/graphql',{
                    method:'POST',
                    headers:{
                        'Content-Type':'application/json',
                    },
                    body: JSON.stringify({
                        query:`
                        query getAllHeroContestRate($avgRankTier:Int){
                            allHeroContest(avgRankTier:$avgRankTier){
                                heroId
                                contested
                                totalGames
                                contestRate
                            }}`,
                            variables:{
                                avgRankTier:filterValue.avg_rank_tier||null,
                                
                            }
                    })
                });
                const contestRates  = await contestRateRes.json();
                
                /// fetch all hero data
                
                const variables = {
                    avgRankTier: filterValue.avg_rank_tier ||null,
                    minPlayedOverall: filterValue.min_played,
                    minPlayedRadiant: filterValue.min_played_radiant,
                    minPlayedDire: filterValue.min_played_dire,
                    minWinOverall: filterValue.min_win,
                    minWinRadiant: filterValue.min_win_radiant,
                    minWinDire: filterValue.min_win_dire
                };
                const GET_HERO_STATS = JSON.stringify({
                    query:`
                    query getAllHeroStats($avgRankTier:Int, $minPlayedOverall:Int,$minPlayedRadiant:Int, $minPlayedDire:Int,$minWinOverall:Float,$minWinRadiant:Float,$minWinDire:Float){
                        allHeroStats(avgRankTier:$avgRankTier,minPlayedOverall:$minPlayedOverall, minPlayedRadiant:$minPlayedRadiant,minPlayedDire:$minPlayedDire, minWinOverall:$minWinOverall,minWinRadiant:$minWinRadiant,minWinDire:$minWinDire){
                            heroId
                            totalGames
                            totalWins
                            radiantGames
                            radiantWins
                            direGames
                            direWins
                            overallWinRate
                            radiantWinRate
                            direWinRate
                        }
                        }
                    `,
                variables:variables
            });
            
                const heroesResponse = await fetch('/api/graphql',{
                    method:"POST",
                    headers:{
                        'Content-Type': "application/json",
                    },
                    body: GET_HERO_STATS//JSON.stringify({GET_HERO_STATS,variables}),
                });
                const result = await heroesResponse.json();
                
                if(result.errors){
                    throw new Error(result.errors.map(err=>err.message).join(', '));
                }
                
                const heroesData =result.data.allHeroStats;
                //need to present the data in the same form as it was in REST endpoint so there isn't a need to redo dependant components 
                const mergedData = heroes.map(hero=>{
                    const stats = heroesData.find(stat=>stat.heroId===hero.heroId) ||{};
                    return {
                        hero: {
                          hero_id: hero.heroId,
                          img_full: hero.imgFull || "", // Assuming imgFull may not be provided
                          img_small: hero.imgSmall,
                          localized_name: hero.localizedName
                        },
                        heroData: {
                          dire_win_rate: stats.direWinRate ,
                          games_won_dire: stats.direWins ,
                          games_won_radiant: stats.radiantWins ,
                          overall_win_rate: stats.overallWinRate ,
                          radiant_win_rate: stats.radiantWinRate ,
                          total_contested: contestRates.data.allHeroContest.find(rate=>rate.heroId===hero.heroId).contested, //using this field as the herotable component still runs the rest endpoint and requires it this way. TODO adjust both
                          total_dire_games: stats.direGames ,
                          total_games: stats.totalGames ,
                          total_radiant_games: stats.radiantGames ,
                          total_wins: stats.totalWins ,                       
                         }
                      };
                });
                setData(mergedData);
                setLoading(false);
            }catch(error){
                console.error("Error fetching data:",error);
                setLoading(false);
            }
        };
        fetchData();
    },[filterValue]);
    return {data,loading, totalGames};
};

//handle rendering
const GraphQLTables= ()=>{
    
    const [filterValue, setFilterValue] = useState({avg_rank_tier:'',min_played:0,min_win:0,min_played_radiant:0,min_win_radiant:0,min_played_dire:0,min_win_dire:0}); 
    const {data ,loading, totalGames} = useFetchData(filterValue);
    const [visibleColumns, setVisibleColumns] = useState(columnOptions.map(opt=>opt.value));

    //have some indication of loading
    if(loading) return <p>Loading.....</p>
    
    return (
        <div className='tables-container'>
            <h1>Tables</h1>
            <div className='table-header'>
                <p className='page-header-description'>Based on {totalGames} games</p>
                <HeroTableFilter setFilterValue={setFilterValue}  maxGames={totalGames} setVisibleColumns={setVisibleColumns}/>
            </div>
            <HeroTable data={data} filterValue={filterValue} visibleColumns={visibleColumns} totalGames={totalGames}/>
        </div>
    );
};

export default GraphQLTables;