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
    'sufficiency': ['Достатність', 'матеріалів'],
    'questions_available': ['Надання', 'питань до заліку'],
    'conformity': ['Відповідність', 'практик лекціям'],
    'punctuality': ['Пунктуальність'],
    'comfort': ['Зручність', 'здачі завдань'],
    'politeness': ['Ввічливість'],
    'relevance': ['Актуальність', 'матеріалу'],
    'cheating': ['Не ставить бали', 'без знань'],
    'timely_informing': ['Своєчасність', 'та достатність', 'інформування'],
    "objectivity": ['Об\'єктивність', 'оцінювання'],
}
const lectorPracticSpecial = new Set([
    'punctuality',    'cheating',    'timely_informing',    "objectivity",
  ])

export const captions = (type, label) => {
    let label_ = label.replace(' *', '')
    let l = captions_[label_].slice()

    if (type === 'lector_practic' && lectorPracticSpecial.has(label_))
        l.push(label.slice(-1) === '*' ? '(практик)' : '(лектор)')

    return l
}