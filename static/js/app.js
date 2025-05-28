function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const csrftoken = getCookie('csrftoken')

function setupLikeButtons(buttons, objectType, action) {
    for (const item of buttons) {
        item.addEventListener('click', (e) => {
            const id = item.dataset[`${objectType}${action.charAt(0).toUpperCase() + action.slice(1)}Id`];
            const url = `/${objectType}/${id}/like`;

            const formData = new FormData();
            formData.append('action', action.includes('dislike') ? 'dislike' : 'like');

            const request = new Request(
                url,
                {
                    method: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    mode: 'same-origin',
                    body: formData
                }
            );
            
            fetch(request).then(response => {
                response.json().then((data) => {
                    const likeCounter = document.querySelector(`span[data-like-counter="${id}"]`);
                    const dislikeCounter = document.querySelector(`span[data-dislike-counter="${id}"]`);
                    likeCounter.innerText = data.likes_count;
                    dislikeCounter.innerText = data.dislikes_count;
                })
            })
        });
    }
}

function onRightAnswerClick(event) {
    const answerId = event.target.dataset.answerId;
    const questionId = event.target.dataset.questionId;
    const url = `/answer/${answerId}/mark_correct/`;

    const formData = new FormData();
    formData.append('is_correct', event.target.checked);
    formData.append('question', questionId);

    const request = new Request(
        url,
        {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin',
            body: formData
        }
    );

    fetch(request).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        const label = document.querySelector(`label[for="btn-check${answerId}"]`);
        if (data.is_correct) {
            label.classList.add('active');
        } else {
            label.classList.remove('active');
        }
        event.target.checked = data.is_correct;
    }).catch(error => {
        console.error('Error:', error);
        event.target.checked = !event.target.checked;
    });
}

function init() {
    const questionLikeButtons = document.querySelectorAll('button[data-question-like-id]');
    const questionDislikeButtons = document.querySelectorAll('button[data-question-dislike-id]');
    setupLikeButtons(questionLikeButtons, 'question', 'like');
    setupLikeButtons(questionDislikeButtons, 'question', 'dislike');

    const answerLikeButtons = document.querySelectorAll('button[data-answer-like-id]');
    const answerDislikeButtons = document.querySelectorAll('button[data-answer-dislike-id]');
    setupLikeButtons(answerLikeButtons, 'answer', 'like');
    setupLikeButtons(answerDislikeButtons, 'answer', 'dislike')

}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}