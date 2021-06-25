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
    })

    document.querySelectorAll('.like_btn_replacement').forEach(ele =>{
        ele.addEventListener('click', function(){
            this.innerHTML = 'really? you narcissist. :/';
        })
    })
})


// ==========================================================================================
// TOGGLING (likes and followers)
// ------------------------------------------------------------------------------------------

// Toggle the status of something, updating the database and the page.
function toggle(e){

    // Stop the page from reloading afterwards
    e.preventDefault();

    // Determine the toggled status
    const previous_status = e.target.dataset.status;
    if (previous_status === 'true' || previous_status === 'false'){
        // Toggling, so reverse the current status
        var toggled_status = previous_status === 'false';

    } else {
        // Something went wrong with loading the button so .dataset.status is still a default value
        console.log('Error: Toggle button failed to load (status is not a boolean).');
        return;
    }

    // Prepare for CSRF validation
    var csrftoken = getCookie('csrftoken');
    var headers = new Headers();
    headers.append('X-CSRFToken', csrftoken);

    // Send to server
    const view_name = e.target.dataset.viewname;
    fetch(`/${view_name}/${e.target.dataset.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            'toggled_status': toggled_status
        }),
        headers: headers,
        credentials: 'include'
    })
    .then(() => {
        update_toggled_page(view_name, toggled_status, e);
    })
    .catch(error =>{
        console.log('Error: ', error);
    });
    
}

// Increment or decrement a counter span.
function update_counter(want_increment, span_id){
    const counter_span = document.querySelector(`#${span_id}`);
    if (counter_span){
        var cval = parseInt(counter_span.innerHTML);
        if (want_increment){
            cval++;
        } else {
            cval--;
        }
        counter_span.innerHTML = cval;
    }
}

// Update the page
function update_toggled_page(toggle_type, toggled_status, e){
    if (toggle_type === 'follow'){
        update_follow_btn(toggled_status);
        update_counter(toggled_status, 'num-followers');

    } else if (toggle_type === 'likes'){
        update_like_button(e.target, toggled_status);
        update_counter(toggled_status, `num_likes_${e.target.dataset.id}`);
    }
}


// ==========================================================================================
// LIKES
// ------------------------------------------------------------------------------------------

// Check database to get the initial like status for this post, then update the button
function load_like_button(btn){

    // Add toggle event when clicked
    btn.addEventListener('click', function(e) {
        toggle(e);
    })

    // Set initial display value
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
    if (is_liked){
        btn.classList.remove('unliked');
        btn.classList.add('liked');
    } else {
        btn.classList.remove('liked');
        btn.classList.add('unliked');       
    }  
    btn.blur();
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
    save_btn.className = 'my-btn';
    save_btn.id = 'save-post-btn';
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
    btn.style.display = 'inline';
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