function Followers(props){
    // Constants that might need altering
    const DISPLAY_TRUE = 'following';
    const DISPLAY_FALSE = 'not following';
    const CLASS_BOTH = 'follow-btn ';
    const CLASS_TRUE = 'following';
    const CLASS_FALSE = 'notfollowing';

    // Initialise with the help of global values from Django
    const [followers, setFollowers] = React.useState({
        num_followers: num_followers,
        display_str: get_display_str(is_following),
        class_list: get_class_list(is_following),
        following: is_following
    });

    // Select the display string to appear inside the button
    function get_display_str(isf){
        if ('true' === isf){
            return DISPLAY_TRUE;
        } else {
            return DISPLAY_FALSE;
        }
    }

    // Select the CSS class list for the button
    function get_class_list(isf){
        if ('true' === isf){
            return CLASS_BOTH + CLASS_TRUE;
        } else {
            return CLASS_BOTH + CLASS_FALSE;
        }
    }

    // Toggle following status
    function toggleFollowers(e){
        // Update follow status on the backend via the toggle function
        toggle(e);

        // Update follow status on the front end
        // Set the new status and increment/decrement number of followers
        var updated_followers = followers.num_followers;
        var toggled = 'true';
        if ('true' === followers.following){
            toggled = 'false';
            updated_followers--;
        } else {
            updated_followers++;
        }

        // Update the state accordingly
        setFollowers({
            num_followers: updated_followers,
            display_str: get_display_str(toggled),
            class_list: get_class_list(toggled),
            following: toggled
        });
    }

    // Display on the page
    if('True' === user_isauth && (username != profile)){
        return (
            <div>
                <FollowerCounter count={followers.num_followers} />
                <button id="follower_toggle_react" class={followers.class_list} data-id={user_id} data-status={followers.following} data-viewname="follow" onClick={(e) => {toggleFollowers(e)}}>{followers.display_str}</button>
            </div>
        );
    }

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
