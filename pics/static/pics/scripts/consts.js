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
    eng: {
        backgroundColor: '#56cc91b4',
        fontColor: '#e7fff3',
        backdropColor: '#081a0e',
    }
}

const captions_ = {
    'cheating_l': ['Не ставить бали', 'без знань', '(лектор)'],
    'cheating_p': ['Не ставить бали', 'без знань', '(практик)'],
    'comfort': ['Зручність', 'здачі завдань'],
    'conformity': ['Відповідність', 'практик лекціям'],
    'find_out_rating': ['Доступ', 'до оцінок'],
    'politeness': ['Ввічливість'],
    'punctuality': ['Пунктуальність'],
    'questions_available': ['Надання', 'питань до заліку'],
    'relevance': ['Актуальність', 'матеріалу'],
    'sufficiency': ['Достатність', 'матеріалів'],
}

export const captions = (type, label) => {
    let label_ = label.replace(' *', '')
    let l = captions_[label_].slice()

    if (type === 'lector_practic' && lectorPracticSpecial.has(label_))
        l.push(label.slice(-1) === '*' ? '(практик)' : '(лектор)')

    return l
}