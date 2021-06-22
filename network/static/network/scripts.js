document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to any/all edit buttons
    document.querySelectorAll('.edit_btn').forEach(btn => {
        btn.addEventListener('click', function() {
            post_edit_mode(this.dataset.id);
        });
    });
})

// EDIT BUTTON ----------------------------------------------------------------
function get_edit_div_id(post_id){
    // Format for the content container div ID
    return `#post_content_${post_id}`;
}

function get_edit_btn_id(post_id){
    // Format for the edit button ID
    return `#edit_btn_${post_id}`;
}

function post_edit_mode(post_id){
    // Replace the post text with a textarea and a save button.
    // Grab the div for the contents
    cont_div = document.querySelector(get_edit_div_id(post_id));
  
    // Make a form
    edit_form = document.createElement('form');

    // Make a textarea element and add it to the form
    txta = document.createElement('textarea');
    txta.innerHTML = cont_div.innerHTML.trim();
    edit_form.append(txta);

    // Make a save button element with an event handler and add it to the form
    save_btn = document.createElement('input');
    save_btn.type = 'submit';
    save_btn.value = 'save';
    save_btn.addEventListener('click', function(e){
        update_post(e, post_id);
    });
    edit_form.append(save_btn);

    // Clear out any old innerHTML, then add the form
    cont_div.innerHTML = '';
    cont_div.append(edit_form);

    // Hide the edit button to prevent user from clicking it again and getting HTML in their textarea
    btn = document.querySelector(get_edit_btn_id(post_id));
    btn.style.display = 'none';
}

function update_post(e, post_id){
    // Update the content of a post, both on the page and in the database.
    // Stop the page from reloading after this
    e.preventDefault();

    // Grab the new text from the textarea
    cont_div = document.querySelector(get_edit_div_id(post_id));
    txa = cont_div.querySelector('textarea');
    editted_content = txa.value.trim();

    // Prepare for CSRF authentication
    var csrftoken = getCookie('csrftoken');
    var headers = new Headers();
    headers.append('X-CSRFToken', csrftoken);

    // PUT it into the database and call function to handle the page
    fetch('/posts', {
        method: 'PUT',
        body: JSON.stringify({
            "id": post_id,
            "editted_content": editted_content
        }),
        headers: headers,
        credentials: 'include'
    })
    .then(post_read_mode(post_id, editted_content))
    .catch(error =>{
        console.log('Error: ', error);
    });
   
}

function post_read_mode(post_id, editted_content){
    // Revert the post to "read mode".
    // Replace the insides of the content div with the content
    cont_div = document.querySelector(get_edit_div_id(post_id));
    cont_div.innerHTML = editted_content;

    // Unhide the edit button
    btn = document.querySelector(get_edit_btn_id(post_id));
    btn.style.display = 'block';
}



// GENERAL USE ----------------------------------------------------------------
function getCookie(name) {
    // Gets a cookie.
    // Taken from Django documentation for CSRF handling
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