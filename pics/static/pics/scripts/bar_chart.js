'use strict'

import {styles} from './consts.js'

export const barChart = (id, dataObject, type) => {
    const canv = document.getElementById(id);
    if (canv === null) return

    new Chart(canv.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['1', '2', '3', '4', '5'],
            datasets: [{
                data: dataObject,
                backgroundColor: styles[type].backgroundColor,
                id: 'y-axis-marks'
            }]
        },
        options: getBarChartOptions(type)
    });
}


const getBarChartOptions = type => (
    {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: styles[type].fontColor,
                    fontSize: 25,
                    maxTicksLimit: 6
                },
                gridLines: {display: false},
            }],
            xAxes: [{
                ticks: {
                    fontColor: styles[type].fontColor,
                    fontSize: 25,
                },
                gridLines: {display: false},
            }]
        },
        legend: {display: false},
        animation: false
    }
)
