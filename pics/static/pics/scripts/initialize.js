'use strict'

import {barChart} from './bar_chart.js';
import {radialDiagram} from './radial.js';
import {setLeftMark} from "./marks.js";
import {styles} from "./consts.js";


const {type, answers} = teacherData;

if (type === "eng") {
    barChart('education-quality-lector', answers['quality'], type)

    setLeftMark('mark-cheating', answers['cheating']);
    setLeftMark('mark-want_to_continue_l', answers['want_to_continue'])

    setResponses(teacherData.responses[0])
} else {
    barChart('education-quality-lector', answers['quality_l'], type)
    barChart('education-quality-practic', answers['quality_p'], type)

    setLeftMark('mark-cheating', answers['cheating_l'])
    setLeftMark('mark-want_to_continue_l', answers['want_to_continue_l'])
    setLeftMark('mark-want_to_continue_p', answers['want_to_continue_p'])

    setResponses(teacherData.responses.join(' / '))
}

barChart('self-assesment', answers['self_rating'], type)

setLeftMark('mark-skills', answers['skills'])
setLeftMark('mark-grading_system', answers['grading_system'])
setLeftMark('mark-meaningfulness', answers['meaningfulness'])

radialDiagram('radial-diagram', answers, type);


function setResponses(responses) {
    document.getElementById("responses").innerText = responses
}


const form = document.getElementById("form")
form.style.color = styles[type].fontColor
form.style.background = styles[type].backdropColor