'use strict'

import {getAvg, getCaption, radialQuestions, styles} from './consts.js'

export const radialDiagram = (id, dataObject, type) => {
    const canv = document.getElementById(id);
    if (canv === null) return

    const [labels, data] = getRadialData(dataObject, type)

    new Chart(canv.getContext('2d'), {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                backgroundColor: styles[type].backgroundColor,
                borderColor: styles[type].fontColor,
                data: data,
            }]
        },
        options: {
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
            legend: {display: false},
            animation: false
        }
    });
}


function getRadialData(obj, type) {
    radialQuestions[type].map(q => console.assert(obj[q] !== undefined, q));
    const labels = radialQuestions[type].map(q => getCaption(q));
    const data = radialQuestions[type].map(q => getAvg(obj[q]));

    return [labels, data];
}

