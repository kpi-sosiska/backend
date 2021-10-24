'use strict'

import {barChart} from './bar_chart.js';
import {radialDiagram} from './radial.js';
import {setLeftMark} from "./marks.js";
import {styles} from "./consts.js";


const {type, answers} = teacherData;

if (type === "lector_practic") {
    barChart('education-quality-lector', answers['quality_l'], type)  // todo appears on hover ???
    barChart('education-quality-practic', answers['quality_p'], type)

    setLeftMark('mark-want_to_continue_l', answers['want_to_continue_l'])
    setLeftMark('mark-want_to_continue_p', answers['want_to_continue_p'])

    // todo
    // setLeftMark('mark-cheating', answers['cheating']);
} else {
    barChart('education-quality-lector', answers['quality'], type)
    setLeftMark('mark-want_to_continue', answers['want_to_continue'])
    setLeftMark('mark-cheating', answers['cheating']);
}

barChart('self-assesment', answers['self_rating'], type)
barChart('education-quality-lector', answers['quality'], type)

setLeftMark('mark-skills', answers['skills'])
setLeftMark('mark-grading_system', answers['grading_system'])
setLeftMark('mark-meaningfulness', answers['meaningfulness'])

radialDiagram('radial-diagram', answers, type);

setResponses(teacherData.responses);
setFormColor();

function setResponses(responses) {
    const r = (type === 'eng') ? responses[0] : responses.join(' / ');
    document.getElementById("responses").innerText = r
}

function setFormColor() {
    const form = document.getElementById("form")
    form.style.color = styles[type].fontColor
    form.style.background = styles[type].backdropColor
}