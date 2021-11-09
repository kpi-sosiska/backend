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

export const captions = {
    'cheating': ['Не ставить бали', 'без знань'],
    'comfort': ['Зручність', 'здачі завдань'],
    'conformity': ['Відповідність', 'практик лекціям'],
    'find_out_rating': ['Доступ', 'до оцінок'],
    'politeness': ['Ввічливість'],
    'punctuality': ['Пунктуальність'],
    'questions_available': ['Надання', 'питань до заліку'],
    'relevance': ['Актуальність', 'матеріалу'],
    'sufficiency': ['Достатність', 'матеріалів'],
    'grading_system': ['Об\'єктивість', 'оцінювання'],
    'meaningfulness': ['Змістовність', 'лекцій'],
    'skills': ['Володіння', 'матеріалом']
}

export const radialQuestions = {  // questions order important!
    eng: ['meaningfulness', 'cheating', 'comfort', 'find_out_rating', 'politeness', 'punctuality', 'questions_available', 'relevance', 'sufficiency', 'grading_system'],
    lector: ['grading_system', 'meaningfulness', 'comfort', 'conformity', 'find_out_rating', 'politeness', 'punctuality', 'questions_available', 'relevance', 'sufficiency', 'grading_system'],
    practic: ['comfort', 'find_out_rating', 'politeness', 'punctuality', 'relevance', 'grading_system', 'skills'],
    lector_practic: ['grading_system', 'meaningfulness', 'skills', 'cheating_l', 'comfort', 'conformity', 'find_out_rating', 'politeness', 'punctuality', 'questions_available', 'relevance', 'sufficiency', 'cheating_p'],
}


export function getCaption(q) {
    const l = q.replace('_l', '').replace('_p', '');
    let label = captions[l].slice() // copy

    if (q.endsWith('_l')) label.push('(лектор)')
    if (q.endsWith('_p')) label.push('(практик)')
    return label
}
