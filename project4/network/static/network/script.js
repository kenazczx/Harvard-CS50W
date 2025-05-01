document.addEventListener('DOMContentLoaded', function() {
    likeButton = document.querySelectorAll('.like-button').forEach((button) => {
        button.addEventListener('click', () => {
            const icon = button.querySelector('i');
            const postId = button.parentElement.dataset.postId;
            fetch(`/like/${postId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                icon.classList.toggle('fa-solid', data.liked);
                icon.classList.toggle('fa-regular', !data.liked);

                const counter = button.closest('[data-post-id]').querySelector('.like-count');
                counter.innerHTML = data.likes_count;
            })
        })   
    })
    editButton = document.querySelectorAll('.edit-button').forEach((button) => {
        button.addEventListener('click', () => {
            const postDiv = button.parentElement;
            const postId = postDiv.dataset.postId;
            const postTextElement = postDiv.querySelector('.post-text');
            const currentText = postTextElement.innerText;

            const textarea = document.createElement('textarea');
            textarea.value = currentText;
            textarea.rows = 3;
            textarea.className = 'form-control';

            const saveButton = document.createElement('button');
            saveButton.innerText = 'Save';
            saveButton.className = 'btn btn-primary';

            postDiv.replaceChild(textarea, postTextElement);
            button.style.display = 'none';
            postDiv.appendChild(saveButton);

            saveButton.addEventListener('click', () => {
                fetch(`/edit-post/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        text: textarea.value,
                    }),
                    })
                    .then((response) => {
                        if (!response.ok) throw new Error('Failed to save');
                        return response.json();
                    })
                    .then((data) => {
                        const newText = document.createElement('p');
                        newText.innerText = data.text;
                        newText.className = 'post-text';

                        postDiv.replaceChild(newText, textarea)
                        saveButton.remove();
                        button.style.display = 'inline-block';
                    })
                })
            })
        })
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
                }
            }
        }
        return cookieValue;
    }
})