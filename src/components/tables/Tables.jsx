/* separate hook 
import {useState, useEffect} from 'react';
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
                const heroResponse = await fetch('/api/populate_hero_list');
                const heroes = await heroResponse.json();
            
                //get total matches
                const countResponse = await fetch(`/api/matches_count?avg_rank_tier=${filterValue.avg_rank_tier}`);
                const countData = await countResponse.json();
                setTotalGames(countData.count);
                //map data for each hero
                const heroDataPromise = heroes.map(async(hero)=>{
                    const heroResponse = await fetch(`/api/populate_hero_table?hero_id=${hero.hero_id}&avg_rank_tier=${filterValue.avg_rank_tier}&min_played_overall=${filterValue.min_played}&min_played_radiant=${filterValue.min_played_radiant}&min_played_dire=${filterValue.min_played_dire}&min_win_overall=${filterValue.min_win}&min_win_radiant=${filterValue.min_win_radiant}&min_win_dire=${filterValue.min_win_dire}`);
                    const heroData = await heroResponse.json();
                    return {hero, heroData};
                });
                //wait for completion and set data
                const heroesData = await Promise.all(heroDataPromise);
                
                setData(heroesData);
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
const Tables= ()=>{
    
    const [filterValue, setFilterValue] = useState({avg_rank_tier:'',min_played:0,min_win:0,min_played_radiant:0,min_win_radiant:0,min_played_dire:0,min_win_dire:0}); 
    const {data ,loading, totalGames} = useFetchData(filterValue);
    const [visibleColumns, setVisibleColumns] = useState(columnOptions.map(opt=>opt.value));
    
    //have some indication of loading
    if(loading) return <p>Loading.....</p>;
    
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

export default Tables;

*/
import { useState, useEffect } from 'react';
import './tables.css';
import './HeroFilter.css';
import HeroTableFilter, { columnOptions } from './HeroTableFilter';
import HeroTable from './HeroTable';

//handle rendering
const Tables = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [totalGames, setTotalGames] = useState(0);
    const [filterValue, setFilterValue] = useState({
        avg_rank_tier: '',
        min_played: 0,
        min_win: 0,
        min_played_radiant: 0,
        min_win_radiant: 0,
        min_played_dire: 0,
        min_win_dire: 0,
    });
    const [visibleColumns, setVisibleColumns] = useState(columnOptions.map(opt => opt.value));

    // Custom hook moved inside Tables component
    const fetchData = async () => {
        try {
            // Populate all heroes
            const heroResponse = await fetch('/api/populate_hero_list');
            const heroes = await heroResponse.json();

            // Get total matches
            const countResponse = await fetch(`/api/matches_count?avg_rank_tier=${filterValue.avg_rank_tier}`);
            const countData = await countResponse.json();
            setTotalGames(countData.count);

            // Map data for each hero
            const heroDataPromise = heroes.map(async (hero) => {
                const heroResponse = await fetch(`/api/populate_hero_table?hero_id=${hero.hero_id}&avg_rank_tier=${filterValue.avg_rank_tier}&min_played_overall=${filterValue.min_played}&min_played_radiant=${filterValue.min_played_radiant}&min_played_dire=${filterValue.min_played_dire}&min_win_overall=${filterValue.min_win}&min_win_radiant=${filterValue.min_win_radiant}&min_win_dire=${filterValue.min_win_dire}`);
                const heroData = await heroResponse.json();
                return { hero, heroData };
            });

            // Wait for completion and set data
            const heroesData = await Promise.all(heroDataPromise);
            setData(heroesData);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [filterValue]);

    // Have some indication of loading
    if (loading) return <p>Loading.....</p>;

    return (
        <div className='tables-container'>
            <h1>Tables</h1>
            <div className='table-header'>
                <p className='page-header-description'>Based on {totalGames} games</p>
                <HeroTableFilter setFilterValue={setFilterValue} maxGames={totalGames} setVisibleColumns={setVisibleColumns} />
            </div>
            <HeroTable data={data} filterValue={filterValue} visibleColumns={visibleColumns} totalGames={totalGames} />
        </div>
    );
};

export default Tables;
