'use strict'

import {getCaption, radialQuestions, styles} from "./consts.js";


const {type, answers} = teacherData;

function main() {

    console.log(answers, type);

    if (type === "lector_practic") {
        barChart('education-quality_l', answers['quality_l'], type)
        barChart('education-quality_p', answers['quality_p'], type)

        leftMark('mark-want_to_continue', mergeAnswers(answers['want_to_continue_l'], answers['want_to_continue_p']))
        leftMark('mark-cheating', mergeAnswers(answers['cheating_l'], answers['cheating_p']))
    } else {
        barChart('education-quality-lector', answers['quality'], type)
        leftMark('mark-want_to_continue', answers['want_to_continue'])
        leftMark('mark-cheating', answers['cheating']);

        leftMark('mark-grading_system', answers['grading_system'])
        leftMark('mark-meaningfulness', answers['meaningfulness'])
    }
    barChart('self-rating', answers['self_rating'], type)
    barChart('education-quality', answers['quality'], type)
    radialDiagram('radial-diagram', answers, type);
    setResponses(teacherData.responses);
    setFormColor();
}

function leftMark(id, value) {
    const el = document.getElementById(id);
    if (el === null) return

    value = getAvg(value) / value.length;

    el.style.color = `hsl(${value ** 2 * 120}deg, 100%, 45%)`
    el.innerHTML = Math.round(value * 100).toString();
}


function radialDiagram(id, obj, type) {
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
    const r = responses.reduce((prev, curr) => prev + curr) //sum of all responses
    document.getElementById("responses").innerText = r
}

function setFormColor() {
    const form = document.getElementById("form")
    form.style.color = styles[type].fontColor
    form.style.background = styles[type].backdropColor
}


function getAvg(answers) {
    // avg([0, 2, 4, 6, 3]) = (1*0 + 2*2 + 3*4 + 4*6 + 5*3) / (0 + 2 + 4  + 6 + 3)
    return answers.reduce((sum, value, i) => sum + (i + 1) * value) /
        answers.reduce((sum, value) => sum + value)
}

function mergeAnswers(a1, a2) {
    console.assert(a1.length === a2.length);
    return a1.slice().map((v, i) => v + a2[i]);
}


main();