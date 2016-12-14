$(function() {
    $.ajax({
        url: '/getPost',
        type: 'GET',
        success: function(res) {
            console.log(res);
            var div = $('<div>').attr('class', 'list-group')
                .append(
                    $('<a id=postLink>').attr('class', 'list-group-item')
                        .append(
                        $('<h2 id="postHeading">').attr('class', 'list-group-item-heading'),
                        $('<a id="user" style="font-size:20px">').attr('class', 'list-group-item-text'),
                        $('<p id="meetingTime">').attr('class', 'list-group-item-text'),
                        $('<p id="location">').attr('class', 'list-group-item-text'),
                        $('<p id="desc">').attr('class', 'list-group-item-text'),
                        $('<p id="postTime" style="font-size:12px; text-align:right">').attr('class', 'list-group-item-text')),
                    // Separated in case we decide to add an interested link to the post itself
                    ($('<p id="interested" style="font-size:16px; text-align:right">').attr('class', 'list-group-item')));

            var postObj = JSON.parse(res);
            var post = '';

            $.each(postObj, function(index, value) {
                post = $(div).clone();
                $(post).addClass(value.Filter);
                $(post).find('#postLink').attr("href", "/post/"+value.PostId);
                $(post).find('#postHeading').text(value.Headline);
                $(post).find('#user').attr("href", "/user/"+value.UserId).text("WHO: " +value.User);
                $(post).find('#meetingTime').text("WHEN: " +value.MeetingTime);
                $(post).find('#location').text("WHERE: " +value.Location);
                $(post).find('#desc').text("WHAT'S UP: " +value.Description);
                $(post).find('#postTime').text("Posted: " +value.PostTime);
                $(post).find('#interested').text("People Interested");
                $('.posts').append(post);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});


$(document).ready(function() {
    $('#filter-following').click(function() {

        if (document.getElementById('filter-following').checked) {
            $('.filter').hide(200);
            console.log("ok");
        }
        else {
            $('.filter').show(200);
        }

    }); 
});
