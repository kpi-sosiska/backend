'use strict'

import {getAvg, getCaption, radialQuestions, styles} from "./consts.js";


const {type, answers} = teacherData;

function main() {
    if (type === "lector_practic") {
        barChart('education-quality_l', answers['quality_l'], type)
        barChart('education-quality_p', answers['quality_p'], type)

        leftMark('mark-want_to_continue_l', answers['want_to_continue_l'])
        leftMark('mark-want_to_continue_p', answers['want_to_continue_p'])

        // todo
        // leftMark('mark-cheating', answers['cheating']);
    } else {
        barChart('education-quality-lector', answers['quality'], type)
        leftMark('mark-want_to_continue', answers['want_to_continue'])
        leftMark('mark-cheating', answers['cheating']);
    }

    barChart('self-rating', answers['self_rating'], type)
    barChart('education-quality', answers['quality'], type)

    leftMark('mark-skills', answers['skills'])
    leftMark('mark-grading_system', answers['grading_system'])
    leftMark('mark-meaningfulness', answers['meaningfulness'])

    radialDiagram('radial-diagram', answers, type);

    setResponses(teacherData.responses);
    setFormColor();
}

function leftMark(id, value) {
    const el = document.getElementById(id);
    if (el === null) return

    value = getAvg(value) / 5;

    el.style.color = `hsl(${value ** 2 * 120}deg, 100%, 45%)`
    el.innerHTML = Math.round(value * 100).toString();
}


export const radialDiagram = (id, obj, type) => {
    const canv = document.getElementById(id);
    if (canv === null) return

    radialQuestions[type].map(q => console.assert(obj[q] !== undefined, q));
    const labels = radialQuestions[type].map(q => getCaption(q));
    const data = radialQuestions[type].map(q => getAvg(obj[q]));

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

function barChart(id, dataObject, type) {
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
        options: {
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
    });
}

function setResponses(responses) {
    const r = (type === 'eng') ? responses[0] : responses.join(' / ');
    document.getElementById("responses").innerText = r
}

function setFormColor() {
    const form = document.getElementById("form")
    form.style.color = styles[type].fontColor
    form.style.background = styles[type].backdropColor
}

main();