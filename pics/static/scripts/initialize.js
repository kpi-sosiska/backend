'use strict'

import { barChart } from './bar_chart.js';
import { radialDiagram } from './radial.js';
import { updateMarkColor } from './single_mark.js';

barChart('education-quality-lector', teacherData.barChart['Якість викладання'], teacherData.type)
barChart('education-quality-practic', teacherData.barChart['Якість викладання *'], teacherData.type)
barChart('self-assesment', teacherData.barChart['Як ви оцінюєте свій рівень'], teacherData.type)

radialDiagram('radial-diagram', teacherData.radial, teacherData.type);

updateMarkColor()
