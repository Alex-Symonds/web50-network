function Followers(){
    // Constants that might need altering
    const DISPLAY_TRUE = 'following';
    const DISPLAY_FALSE = 'not following';
    
    const CLASS_BOTH = 'follow-btn';
    const CLASS_TRUE = 'following';
    const CLASS_FALSE = 'notfollowing';

    // Initialise with the help of global values from Django
    const [followers, setFollowers] = React.useState({
        num_followers: num_followers,
        following: str_following === 'true',
        display_str: get_display_str(str_following === 'true'),
        class_list: get_class_list(str_following === 'true')
    });

    // Select the display string to appear inside the button
    function get_display_str(isf){
        if (isf){
            return DISPLAY_TRUE;
        } else {
            return DISPLAY_FALSE;
        }
    }

    // Select the CSS class list for the button
    function get_class_list(isf){
        if (isf){
            return CLASS_BOTH + ' ' + CLASS_TRUE;
        } else {
            return CLASS_BOTH + ' ' + CLASS_FALSE;
        }
    }

    // Toggle "following" status
    function toggleFollowers(e){
        // Update follow status on the backend via the toggle function
        toggle(e);

        // Update follow status on the front end
        // Set the new status and increment/decrement number of followers
        var updated_followers = followers.num_followers;
        var toggled = true;
        if (followers.following){
            toggled = false;
            updated_followers--;
        } else {
            updated_followers++;
        }

        // Update the state accordingly
        setFollowers({
            num_followers: updated_followers,
            following: toggled,
            display_str: get_display_str(toggled),
            class_list: get_class_list(toggled)
        });
    }

    //If the user is logged in and it's not their own profile, display the counter and the toggle button
    if('True' === user_isauth && (username != profile)){
        return [
                <FollowerCounter count={followers.num_followers} />,
                <button id="follower_toggle_react" class={followers.class_list} data-id={user_id} data-status={followers.following} data-viewname="follow" onClick={(e) => {toggleFollowers(e)}}>{followers.display_str}</button>
        ];
    }
    // Otherwise, just display the counter
    return <FollowerCounter count={followers.num_followers} />;
}

function FollowerCounter(props){
    // Displays the number of current followers in a span
    return (
        <span class="follow-count-num" id="num-followers">
            {props.count}
        </span>
    );   
}

// Render it to the page
ReactDOM.render(<Followers />, document.querySelector("#followers-react"));
