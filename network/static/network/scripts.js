document.addEventListener('DOMContentLoaded', function() {

    if (document.getElementById('follow_btn')){
        load_follow_btn();
    }
})


function load_follow_btn(){
    // Initialise the follow button based on its status in the database.
    // Assumption: URL ends in "/#" where # is the ID of the user to be followed (or not).
    target_id = parseInt(window.location.pathname.split("/").pop());
    
    fetch(`/follow/${target_id}`)
    .then(response => response.json())
    .then(data =>{
        display_follow_btn(data["is_followed"]);
    })
    .catch(error =>{
        console.log('Error: ', error);
    })
}

function display_follow_btn(is_followed){
    // Set the follow button's value and class based on is_followed bool.
    const button = document.querySelector('#follow_btn');
    const st_input = document.querySelector('#follow_status');

    if (is_followed){
        button.value='following';
        button.className='following';
        st_input.value='true';
    }else{
        button.value='not following';
        button.className='not-following';
        st_input.value='false';
    }   
}

function update_followedby_counter(want_follow){
    // Increment or decrement the followers counter based on want_follow.
    counter = document.querySelector('#num-followers');
    if (counter){
        cval = parseInt(counter.innerHTML);
        if (want_follow){
            counter.innerHTML = cval + 1;
        }else{
            counter.innerHTML = cval - 1;
        }
    }
}


function follow_toggle(){
    // Process the toggle form and update database.
    form = document.getElementById('follow_toggle_form');
    target_id = parseInt(form['follow_target_id'].value);
    btn_val = form['follow_btn'].value;

    // Decide on the desired action
    f_status = form['follow_status'].value;
    if (f_status === 'true' || f_status === 'false'){
        // Toggling, so reverse the current status
        result = f_status === 'false';
    } else {
        console.log('Error: ', 'Invalid btn_val');
        return false;       
    }

    // Prepare for CSRF authentication
    var csrftoken = getCookie('csrftoken');
    var headers = new Headers();
    headers.append('X-CSRFToken', csrftoken);

    // Update database and page
    fetch(`/follow/${target_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            "want_follow": result
        }),
        headers: headers,
        credentials: 'include'
    })
    .then(display_follow_btn(result))
    .then(update_followedby_counter(result))
    .catch(error => {
        console.log('Error: ', error)
    });
}


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