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
                        $('<p id="desc">').attr('class', 'list-group-item-text'),
                        $('<p id="user">').attr('class', 'list-group-item-text'),
                        $('<p id="meetingTime">').attr('class', 'list-group-item-text'),
                        $('<p id="location">').attr('class', 'list-group-item-text'),
                        $('<p id="postTime">').attr('class', 'list-group-item-text')
                    ));

            var postObj = JSON.parse(res);
            var post = '';

            $.each(postObj, function(index, value) {
                post = $(div).clone();
                $(post).find('h2').text(value.Headline);
                $(post).find('#desc').text(value.Description);
                $(post).find('#user').text(value.User);
                $(post).find('#meetingTime').text(value.MeetingTime);
                $(post).find('#location').text(value.Location);
                $(post).find('#postTime').text(value.PostTime);
                $('.posts').append(post);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});
