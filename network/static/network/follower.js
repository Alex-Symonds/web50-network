document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('follower_toggle')){
        load_follow_btn(document.getElementById('follower_toggle'));
    }
})

// Initialise the follow button based on its status in the database.
function load_follow_btn(btn){

    // Add toggle event when clicked
    btn.addEventListener('click', (e) =>{
        toggle(e);
    });

    // Set initial display value
    fetch(`/follow/${btn.dataset.id}`)
    .then(response => response.json())
    .then(data =>{
        update_follow_btn(data['is_followed']);
    })
    .catch(error =>{
        console.log('Error: ', error);
    })
}

function update_follow_btn(is_followed){
    // Set the follow button's value and class based on is_followed bool.
    const button = document.querySelector('#follower_toggle');

    if (is_followed){
        button.innerHTML='following';
        button.className='following';
        button.dataset.status=true;
    }else{
        button.innerHTML='not following';
        button.className='not-following';
        button.dataset.status=false;
    }   
}