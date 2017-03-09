var task_failure_message = "That's not the correct answer. But, it's okay! This was just a sample task. Pay more attention when the real task comes. You need to understand the task clearly before being able to explain it to the bot.";

$("#continue").hide()

var form = $('#applet-form')
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
                if(data == "correct") {
                    $( "#continue" ).trigger("click");
                } else {
                    $("#error-message").html(task_failure_message);
                    $("#submit").attr('disabled', true);
                    $("#continue").show();
                }
            },
            error: function(data) {
                $("#error-message").html("Something went wrong!");
            }
        });
        return true;
    }
});

$("#continue").on("click", function(e) {
    $(location).attr('href', sample_conversation_url)
});

function is_valid(form) {
    data = form.serialize()
    js = get_url_vars(data)
    return ('trigger_fn' in js && 'action_fn' in js &&
            'trigger_channel' in js && 'action_channel' in js)
}
