'use strict'

import {styles} from "./consts.js";

const getHsl = (coef) => `hsl(${coef*coef*120}deg, 100%, 45%)`

const setColor = (el, func) => {
 el.style.color = getHsl(func(+el.innerHTML))
}

export const updateMarksColors = () => {
  for (let el of document.getElementsByClassName("mark-percent"))
    setColor(el, x => x / 100)

  for (let el of document.getElementsByClassName("mark"))
    setColor(el, x => x/5)
}


export const updateFormColors = (type) => {
    const form = document.getElementById("form")
    form.style.color = styles[type].fontColor
    form.style.background = styles[type].backdropColor
}
