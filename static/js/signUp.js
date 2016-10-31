$(function() {
    $('#btnSignUp').click(function() {

        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
                message = $.parseJSON(response)
                if (message["error"]) {
                    $('.error').text('Username exists.');
                    $('.message').text('');
                }
                else if (message["message"]) {
                    $('.error').text('');
                    $('.message').text('Sign up successful.');
                }
            },
            error: function(error) {
                console.log(error);
                $('.error').text('Enter the required fields.');
                $('.message').text('');
            }
        });
    });
});