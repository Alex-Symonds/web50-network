document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to any/all edit buttons
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            post_edit_mode(this.dataset.id);
        });
    });

    // Add event listeners to any/all like buttons
    document.querySelectorAll('.like-btn').forEach(btn => {
        load_like_button(btn);
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
        console.log('"' + e.target.dataset.status + '" = ' + typeof e.target.dataset.status);
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
    .then(response => response.json())
    .then(data => {
        // If the user is not logged in, redirect them to the error page bearing a suitable message.
        // (The server will use the GET parameters to select the correct message.)
        if ('redirect' in data){
            window.location.href = data['redirect'] + '&type=' + view_name;
        }
        else{
            update_toggled_page(view_name, toggled_status, e);
        }
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
    if (toggle_type === 'likes'){
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
        btn.innerHTML = '<span>LIKED</span>';
    } else {
        btn.classList.remove('liked');
        btn.classList.add('unliked'); 
        btn.innerHTML = '<span>LIKE</span>';      
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


// Store the original text. Used to restore the post if the edit fails.
var post_original;

function access_denied_innerHTML(){
    return '<span>ACCESS DENIED</span><br>YOU DO NOT OWN THIS POST.';
}

function access_denied_className(){
    return 'edit-failed';
}

// Replace the post text with a textarea and a save button.
function post_edit_mode(post_id){
    // Grab the div for the contents
    cont_div = document.querySelector(get_edit_div_id(post_id));

    // Make a form
    edit_form = document.createElement('form');

    // Make a textarea element and add it to the form
    txta = document.createElement('textarea');
    //txta.innerHTML = cont_div.innerHTML.trim();
    str_split = cont_div.innerHTML.split("</div>");

    if (str_split.length == 2){
        contents_str = str_split[1];
    } else {
        contents_str = str_split[0];
    }

    txta.innerHTML = contents_str.trim();
    edit_form.append(txta);

    // Save the text in the global variable
    post_original = txta.innerHTML;

    // Make a save button element with an event handler and add it to the form
    save_btn = document.createElement('input');
    save_btn.type = 'submit';
    save_btn.value = 'SAVE';
    save_btn.classList.add('post-btn');
    save_btn.classList.add('lcars-btn');
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

// Update the content of a post, both on the page and in the database.
function update_post(e, post_id){
    
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

    // Put it into the database and call function to handle the page
    fetch('/posts', {
        method: 'PUT',
        body: JSON.stringify({
            "id": post_id,
            "editted_content": editted_content
        }),
        headers: headers,
        credentials: 'include'
    })
    .then(response => {        
        post_read_mode(post_id, editted_content, response.status);
    })
    .catch(error =>{
        console.log('Error: ', error);
    });
   
}

function post_read_mode(post_id, editted_content, http_code){
    // Revert the post to "read mode".
    // Replace the insides of the content div with the content
    cont_div = document.querySelector(get_edit_div_id(post_id));
    cont_div.innerHTML = '';

    // If something went wrong, show an error and return to the uneditted post
    if (http_code != 200){
        let errmsg = document.createElement('div');
        errmsg.innerHTML = access_denied_innerHTML();
        errmsg.className = access_denied_className();
        cont_div.append(errmsg);
        cont_div.append(post_original);

    // Otherwise, update the page to show the editted post
    } else {
        cont_div.innerHTML = editted_content.toUpperCase();
        // Unhide the edit button
        btn = document.querySelector(get_edit_btn_id(post_id));
        btn.style.display = 'inline';
    }
}







// GENERAL USE ----------------------------------------------------------------
function getCookie(name) {
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