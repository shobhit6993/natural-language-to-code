var task_failure_message = "You do not seem to have understood the task correctly. You cannot proceed to chat with the bot. Go ahead and click the 'Get Code' button to get the code.";
var try_again_message = "Incorrect answers. You have %d more attempts.";
var incorrect_counter = 4;

$("#continue").hide()
$("#code").hide()

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
                    if(incorrect_counter > 0) {
                        message = "Incorrect answers. You have " + incorrect_counter + " more attempts.";
                        incorrect_counter -= 1;
                        $("#error-message").html(message);
                    } else {
                        // Log task failure.
                        $.ajax({
                            type: "post",
                            url: fail_url,
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken'),
                                'sessionid':getCookie('sessionid')
                            },
                            error: function(data) {
                                $("#error-message").html("Something went wrong!");
                            }
                        });

                        $("#error-message").html(task_failure_message);
                        $("#submit").attr('disabled', 'disabled');
                        $("#code").show();
                    }
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
    $(location).attr('href', actual_conversation_url)
});

$("#code").on("click", function(e) {
    $(location).attr('href', code_url)
});

function is_valid(form) {
    data = form.serialize()
    js = get_url_vars(data)
    return ('trigger_fn' in js && 'action_fn' in js &&
            'trigger_channel' in js && 'action_channel' in js)
}
