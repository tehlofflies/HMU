$(function() {
    $.ajax({
        url: '/getUsers',
        type: 'GET',
        success: function(res) {
            console.log(res);
            var div = $('<div>')
                .attr('class', 'list-group')
                .append($('<a>')
                    .attr('class', 'list-group-item')
                    .append(
                        $('<h2>').attr('class', 'list-group-item-heading'),
                        $('<p id="email">').attr('class', 'list-group-item-text')
                    ));

            var userObj = JSON.parse(res);
            var user = '';

            $.each(userObj, function(index, value) {
                user = $(div).clone();
                $(user).find('a').attr("href", "/user/"+value.Id);
                $(user).find('h2').text(value.Name);
                $(user).find('#email').text(value.Email);
                $('.users').append(user);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});
