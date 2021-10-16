'use strict'

import { barChart } from './bar_chart.js';
import { radialDiagram } from './radial.js';
import {updateFormColors, updateMarksColors} from "./colors.js";

barChart('education-quality-lector', teacherData.barChart['quality_l'], teacherData.type)
barChart('education-quality-practic', teacherData.barChart['quality_p'], teacherData.type)
barChart('self-assesment', teacherData.barChart['self_rating'], teacherData.type)

radialDiagram('radial-diagram', teacherData.radial, teacherData.type);

updateMarksColors()
updateFormColors(teacherData.type)
