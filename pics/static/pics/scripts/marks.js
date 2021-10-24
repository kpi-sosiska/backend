'use strict'

import {getAvg} from "./consts.js";


export function setLeftMark(id, value) {
    const el = document.getElementById(id);
    if (el === null) return

    value = getAvg(value) / 5;

    el.style.color = getHsl(value)
    el.innerHTML = Math.round(value * 100).toString();
}

const getHsl = (coef) => `hsl(${coef*coef*120}deg, 100%, 45%)`
