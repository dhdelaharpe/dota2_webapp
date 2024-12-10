import React from 'react';
import {Line} from 'react-chartjs-2';
import {Chart, CategoryScale, LinearScale, Filler, PointElement, LineElement, Tooltip, Legend, TimeScale} from 'chart.js';
import 'chartjs-adapter-date-fns';

/// Basic Chart component setup
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, TimeScale, Filler);

const LineChart = ({data,options})=>{
    return(
        <div>
            <Line data={data} options={options}/>
        </div>
    );
};

export default LineChart;