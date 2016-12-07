$(function() {
    $.ajax({
        url: '/getPost',
        type: 'GET',
        success: function(res) {
            console.log(res);
            var div = $('<div>')
                .attr('class', 'list-group')
                .append($('<a>')
                    .attr('class', 'list-group-item')
                    .append(
                        $('<h2>').attr('class', 'list-group-item-heading'),
                        $('<p id="user">').attr('class', 'list-group-item-text'),
                        $('<p id="meetingTime">').attr('class', 'list-group-item-text'),
                        $('<p id="location">').attr('class', 'list-group-item-text'),
                        $('<p id="desc">').attr('class', 'list-group-item-text'),
                        $('<p id="postTime">').attr('class', 'list-group-item-text')
                    ));

            var postObj = JSON.parse(res);
            var post = '';

            $.each(postObj, function(index, value) {
                post = $(div).clone();
                $(post).addClass(value.Filter);
                $(post).find('a').attr("href", "/user/"+value.UserId);
                $(post).find('h2').text(value.Headline);
                $(post).find('#user').text("WHO: " +value.User);
                $(post).find('#meetingTime').text("WHEN: " +value.MeetingTime);
                $(post).find('#location').text("WHERE: " +value.Location);
                $(post).find('#desc').text("WHAT'S UP: " +value.Description);
                $(post).find('#postTime').text("Posted: " +value.PostTime);
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
