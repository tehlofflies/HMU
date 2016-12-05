$(function() {
    $.ajax({
        url: '/getFollowing',
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

            var followingObj = JSON.parse(res);
            var following = '';

            $.each(followingObj, function(index, value) {
                following = $(div).clone();
                $(following).find('a').attr("href", "/user/"+value.FollowedId);
                $(following).find('h2').text(value.FollowedName);
                $('.followings').append(following);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});
