'use strict'

import {barChart} from './bar_chart.js';
import {radialDiagram} from './radial.js';
import {updateFormColors, updateMarksColors} from "./colors.js";

if (teacherData.type === "eng")
    barChart('education-quality-lector', teacherData.answers['quality'], teacherData.type)
else {
    barChart('education-quality-lector', teacherData.answers['quality_l'], teacherData.type)
    barChart('education-quality-practic', teacherData.answers['quality_p'], teacherData.type)
}
barChart('self-assesment', teacherData.answers['self_rating'], teacherData.type)

radialDiagram('radial-diagram', teacherData.answers, teacherData.type);

updateMarksColors()
updateFormColors(teacherData.type)
