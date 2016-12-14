$(function() {
    $.ajax({
        url: '/getFollowers',
        type: 'GET',
        success: function(res) {
            console.log(res);
            var div = $('<div>')
                .attr('class', 'list-group')
                .append($('<a>')
                    .attr('class', 'list-group-item')
                    .append(
                        $('<h2>').attr('class', 'list-group-item-heading')
                    ));

            var followerObj = JSON.parse(res);
            var follower = '';

            $.each(followerObj, function(index, value) {
                follower = $(div).clone();
                $(follower).find('a').attr("href", "/user/"+value.FollowerId);
                $(follower).find('h2').text(value.FollowerName);
                $('.followers').append(follower);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});
