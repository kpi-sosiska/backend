'use strict'

export const styles = {
    lector: {
        backgroundColor: '#48abddb4',
        fontColor: '#e6f7ff',
        backdropColor: '#08141a',
    },
    practic: {
        backgroundColor: '#dfdf39b4',
        fontColor: '#ffffea',
        backdropColor: '#141402',
    },
    lector_practic: {
        backgroundColor: '#dd48ddb4',
        fontColor: '#fee6ff',
        backdropColor: '#19081a',
    },
    english: {
        backgroundColor: '#56cc91b4',
        fontColor: '#e7fff3',
        backdropColor: '#081a0e',
    }
}

const captions_ = {
    'Достатність матеріалів': ['Достатність', 'матеріалів'],
    'Наявність переліку питань': ['Надання', 'питань до заліку'],
    'Відповідність завдань': ['Відповідність', 'практик лекціям'],
    'Пунктуальність': ['Пунктуальність'],
    'Зручність здачі завдань': ['Зручність', 'здачі завдань'],
    'Ввічливість викладача': ['Ввічливість'],
    'Актуальність матеріалу': ['Актуальність', 'матеріалу'],
    'Бали без знань': ['Не ставить бали', 'без знань'],
    'Своєчасність інформування': ['Своєчасність', 'та достатність', 'інформування'],
    "Об'єктивність оцінювання": ['Об\'єктивність', 'оцінювання'],
}
const lectorPracticSpecial = new Set([
    'Пунктуальність',
    'Бали без знань',
    'Своєчасність інформування',
    "Об'єктивність оцінювання",
  ])

export const captions = (type, label) => {
    let label_ = label.replace(' *', '')
    let l = captions_[label_].slice()

    if (type === 'lector_practic' && lectorPracticSpecial.has(label_))
        l.push(label.slice(-1) === '*' ? '(практик)' : '(лектор)')

    return l
}