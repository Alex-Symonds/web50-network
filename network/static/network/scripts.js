document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to any/all edit buttons
    document.querySelectorAll('.edit_btn').forEach(btn => {
        btn.addEventListener('click', function() {
            post_edit_mode(this.dataset.id);
        });
    });

    // Add event listeners to any/all like buttons
    document.querySelectorAll('.like_btn').forEach(btn => {
        load_like_button(btn);
        btn.addEventListener('click', function(e) {
            toggle_like(e);
        })
    })
})


// ==========================================================================================
// LIKES
// ------------------------------------------------------------------------------------------

// Check database to get the initial like status for this post, then update the button
function load_like_button(btn){
    fetch(`/likes/${btn.dataset.id}`)
    .then(response => response.json())
    .then(data => {
        update_like_button(btn, data['liked']);
    })
    .catch(error => {
        console.log('Error: ', error)
    })
}

// Update a like button's properties
function update_like_button(btn, is_liked){
    // Update data-status
    btn.dataset.status = is_liked;

    // Prepare cosmetic settings
    var new_innerHTML = '';
    if (is_liked){
        new_innerHTML = 'liked';
    } else {
        new_innerHTML = '_____';
    } 
    btn.innerHTML = new_innerHTML; 
}

// Increment or decrement a likes counter
function update_like_counter(btn, want_increment){
    const counter_id = `num_likes_${btn.dataset.id}`;
    counter_span = document.querySelector(`#${counter_id}`);

    var counter = parseInt(counter_span.innerHTML);
    if (want_increment){
        counter++;
    } else {
        counter--;
    }

    counter_span.innerHTML = counter;
}

// Toggle like status, updating the database and the page.
function toggle_like(e){

    // Stop the page from reloading afterwards
    e.preventDefault();

    // Reverse the previous status
    const liked_before = e.target.dataset.status;
    if (liked_before == 'true'){
        var like_now = false;
    } else if (liked_before == 'false'){
        var like_now = true;
    } else {
        // Something went wrong with load_like_button(...) and .dataset.status is still the default value
        console.log('Error: Like button failed to load (status is not a boolean).');
        return;
    }

    // Prepare for CSRF validation
    var csrftoken = getCookie('csrftoken');
    var headers = new Headers();
    headers.append('X-CSRFToken', csrftoken);

    // Send to server
    fetch(`/likes/${e.target.dataset.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            'is_liked': like_now
        }),
        headers: headers,
        credentials: 'include'
    })
    .then(() => {
        // Update the page
        update_like_button(e.target, like_now);
        update_like_counter(e.target, like_now);
    })
    .catch(error =>{
        console.log('Error: ', error);
    });
    
}


// ==========================================================================================
// EDIT
// ------------------------------------------------------------------------------------------
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