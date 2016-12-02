// $(function() {
//     $.ajax({
//         url: '/getUserProfile/{{ user_id }}',
//         type: 'GET',
//         success: function(res) {
//             console.log(res);
//         },
//         error: function(error) {
//             console.log(error);
//         }
//     });
// });

$(function() {
    //djangoData = int($('#my-data').data());
    // number = "{{user_id}}";
    $.ajax({
        // url: "{{ url_for('app.getUserProfile(user_id)') }}",
        
        url: '/getUserProfile/2',
        type: 'GET',
        success: function(res) {
            console.log(res);
            var div = $('<div>')
                .attr('class', 'list-group')
                .append($('<a>')
                    .attr('class', 'list-group-item')
                    .append(
                        $('<h2>').attr('class', 'list-group-item-heading'),
                        $('<p id="bio">').attr('class', 'list-group-item-text'),
                        $('<p id="email">').attr('class', 'list-group-item-text'),
                        $('<p id="phone">').attr('class', 'list-group-item-text'),
                        $('<p id="facebook">').attr('class', 'list-group-item-text')
                    ));

            var infoObj = JSON.parse(res);
            var info = '';

            $.each(infoObj, function(index, value) {
                info = $(div).clone();
                $(info).find('h2').text(value.Name);
                $(info).find('#bio').text(value.Bio);
                $(info).find('#email').text(value.Email);
                $(info).find('#phone').text(value.Phone);
                $(info).find('#facebook').text(value.Facebook);
                $('.infos').append(info);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});
