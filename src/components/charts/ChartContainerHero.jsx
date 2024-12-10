import React, {useState, useEffect} from 'react';
import LineChart from './LineChart';
import './ChartContainer.css';

const ChartContainerHero=({heroId, setTotalGames})=>{
    const [chartData,setChartData]= useState({chart1:null,chart2:null,chart3:null});//this draws 3 charts so we need 3
    const [totalRadiantGames,setTotalRadiantGames]= useState(null);
    const [totalDireGames,setTotalDireGames]=useState(null);
    useEffect(()=>{
        const fetchData=async ()=>{
            try{
                const response = await fetch(`/api/hero_win_rate_over_time?interval=day&hero_id=${heroId}`);
                const data = await response.json();
                const round = (num)=> Math.round(num*100)/100;
                const totalDireGames = (data.map(item=>item.total_dire_matches)).reduce((sum,a)=>sum+a,0);
                const totalRadiantGames = (data.map(item=>item.total_radiant_matches)).reduce((sum,a)=>sum+a,0);
                const totalGames= totalDireGames+totalRadiantGames;
                setTotalGames(totalGames);
                setTotalRadiantGames(totalRadiantGames);
                setTotalDireGames(totalDireGames);
                const overallLabels = data.map(item=>item.date);
                const overallValue = data.map(item=>round(item.overall_win_rate));
                const chart1Data={
                    labels:overallLabels,
                    datasets:[{
                        label:"Hero overall win rate",
                        data: overallValue,
                        borderColor: '#aa9f9f',
                        backgroundColor:'#43ff64d9',
                        fill:true,
                    }],
                };
                const chart2Data={
                    labels:overallLabels,
                    datasets:[{
                        label:"Hero radiant win rate",
                        data: data.map(item=>item.radiant_win_rate),
                        borderColor: '#aa9f9f',
                        backgroundColor:'#43ff64d9',
                        fill:true,
                    }],
                };
                const chart3Data={
                    labels:overallLabels,
                    datasets:[{
                        label:"Hero dire win rate",
                        data: data.map(item=>item.dire_win_rate),
                        borderColor: '#aa9f9f',
                        backgroundColor:'#bb012d',
                        fill:true,
                    }],
                };

                setChartData({chart1:chart1Data, chart2:chart2Data, chart3:chart3Data});
            }catch(error){console.error('Error fetching hero data:',error);}
        };
        fetchData();
    },[heroId, setTotalGames]);
    
    const options = {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.dataset.label}: ${context.raw}`;
              },
            },
          },
        },
        scales: {
          x: {
            type: 'time',
            time: { unit: 'day' },
            title: {
              display: true,
              text: 'Date',
            },
          },
          y: {
            beginAtZero: true,
            max:100,
            title: {
              display: true,
              text: '%win rate',
            },
          },
        },
      };
    return(
        <div className='chart-container'>
            <h2>Overall win rate</h2>
            {chartData.chart1? <LineChart data={chartData.chart1} options={options}/>: <p>Loading</p>}
            <h2>Radiant win rate</h2>
            <p>Over {totalRadiantGames ? `${totalRadiantGames}`:'....'} games</p>
            {chartData.chart2? <LineChart data={chartData.chart2} options={options}/>:<p>Loading</p>}
            <h2>Dire win rate</h2>
            <p>Over {totalDireGames?`${totalDireGames}`:'....'} games</p>
            {chartData.chart3? <LineChart data={chartData.chart3} options={options}/>:<p>Loading</p>}
        </div>
    );
};

export default ChartContainerHero;