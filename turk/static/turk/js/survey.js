var form = $('#survey-form')

form.on('submit', function(e) {
    e.preventDefault();
    if (!is_valid(form)) {
        $("#error-message").html("Answer all questions.");
        return false;
    }
    else {
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'sessionid':getCookie('sessionid')
            },
            data: form.serialize(),
            success: function (data) {
                $(location).attr('href', data)
            },
            error: function(data) {
                $("#error-message").html("Something went wrong!");
            }
        });
        return true;
    }
});

function is_valid(form) {
    data = form.serialize()
    js = get_url_vars(data)
    console.log(js)
    return ('easy' in js && 'understand' in js &&
            'sensible' in js && 'long' in js)
}