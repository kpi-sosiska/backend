'use strict'

import {captions, styles} from './consts.js'

const getChartOptions = type => (
    {
        responsive: true,
        maintainAspectRatio: false,
        scale: {
            angleLines: {
                lineWidth: 2,
                color: styles[type].fontColor
            },
            gridLines: {
                lineWidth: 2,
                color: styles[type].fontColor,

            },
            ticks: {
                min: 1, max: 5, stepSize: 1,
                fontSize: 24,
                fontColor: styles[type].fontColor,
                backdropColor: styles[type].backdropColor
            },
            pointLabels: {
                fontSize: 23,
                fontColor: styles[type].fontColor
            }
        },
        legend: {display: false}
    }
)

const extractData = (obj, type) => ({
    labels: Object.keys(obj).map(label => captions(type, label)),
    datasets: [{
        backgroundColor: styles[type].backgroundColor,
        borderColor: styles[type].fontColor,
        data: Object.values(obj),
    }]
})

export const radialDiagram = (id, dataObject, type) => {
    const canv = document.getElementById(id);
    if (canv === null) return

    new Chart(canv.getContext('2d'), {
        type: 'radar',
        data: extractData(dataObject, type),
        options: getChartOptions(type)
    });
}
