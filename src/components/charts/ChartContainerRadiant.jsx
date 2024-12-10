import React, {useState, useEffect} from 'react';
import LineChart from './LineChart';
import './ChartContainer.css';

const ChartContainerRadiant=({setTotalGames})=>{
    const [chartData, setChartData] = useState(null);

    useEffect(()=>{
        const fetchData = async()=>{ // prepare chart data
            try{
              const response = await fetch('/api/radiant_win_rate_over_time?interval=day');
              const data = await response.json();
              
              const totalGames = (data.map(item=>item.total_matches)).reduce((sum,a)=>sum+a,0);
              setTotalGames(totalGames);

              const labels= data.map(item=>item.date);
              const values = data.map(item=>item.win_rate);

              setChartData({
                  labels,
                  datasets:[{
                      label:"Overall win rate",
                      data:values,
                      borderColor: '#aa9f9f',
                      backgroundColor: '#43ff64d9',
                      fill: true,
                  }],
              });
            }catch(error){console.error('Error fetching data:',error);}
        };
        fetchData();
    }, [setTotalGames]);

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
            title: {
              display: true,
              text: '%win rate',
            },
            max:100,
          },
        },
      };

    return(
        <div className='chart-container'>
          <h2>Radiant win rate</h2>
            {chartData? (
              
                <LineChart data={chartData} options={options}/>
            ): (
                <p>Loading</p>
            )}
        </div>
    );
};

export default ChartContainerRadiant;