var table = $("#conversation");
var form = $("#dialog-form");

table.hide();
form.hide();
$("#continue").hide();

$('#start').on('click', function(e) {
    $(this).hide();
    table.show();
    form.show();

    var robot_utterance = "typing..."
    $.ajax({
        type: "GET",
        url: open_dialog_url,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'sessionid':getCookie('sessionid')
        },
        success: function (json_response) {
            robot_utterance_1 = json_response['sys_utterance_1']
            robot_utterance_2 = json_response['sys_utterance_2']
            user_utterance = json_response['user_utterance']
            intent = json_response['intent']

            // Row for robot's first utterance.
            $($("#form-row").prev().find('td')[1]).html(robot_utterance_1)
            // Row for automatically generated user utterance.
            user_row = $('<tr><td style="width:10%">YOU:</td><td style="width:90%">' + user_utterance + '</td></tr>');
            $("#form-row").before(user_row);

            change_color_using_intent(intent)
            // Row for robot's second utterance.
            robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">' + robot_utterance_2 + '</td></tr>');
            $("#form-row").before(robot_row);
            $("#input-box").prop('disabled', false)
            $("#input-box").focus();
        },
        error: function(data) {
            $("#error-message").html("Something went wrong!");
        }
    });

    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">' + robot_utterance + '</td></tr>');
    $("#form-row").before(robot_row);

    // Add input-box for user-utterance.
    form_buttons = '<input type="text" value="" style="width:90%" name="user_utterance" id="input-box" disabled><input type="submit" id="submit" value="Send"><div id="error-message"></div>'
    form.append(form_buttons);
});


form.on('submit', function(e) {
    e.preventDefault();
    var user_utterance = $("#input-box").val()
    if (user_utterance == "") {
        $("#error-message").html("Please enter a message.");
        return false;
    } else if (poor_utterance(user_utterance)) {
        $("#error-message").html("Please use proper English.");
        return false;
    } else {
        $("#error-message").html("");
        $("#input-box").prop('disabled', true);
        convert_form_to_text(user_utterance);
        send_utterance_to_dialog_agent(user_utterance);
        return false;
    }
});

function send_utterance_to_dialog_agent(user_utterance) {
    // Add row for new utterance from robot. For now, show "typing...".
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">typing...</td></tr>');
    $("#form-row").before(robot_row);

    $.ajax({
        type: "POST",
        url: read_user_utterance_url,
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'sessionid':getCookie('sessionid')
        },
        data: {
            'user_utterance': user_utterance,
        },
        success: function (data) {
            robot_utterance = data['system_utterance'];
            intent = data['intent']
            change_color_using_intent(intent)
            $($("#form-row").prev().find('td')[1]).html(robot_utterance);
            if (robot_utterance == "Ok, bye!") {
                // End of dialog.
                $("#form-row").remove();
                $("#continue").show();
            } else {
                $("#input-box").prop('disabled', false);
                $("#input-box").focus();
            }
        },
        error: function(data) {
            $("#error-message").html("Something went wrong!");
        }
    });
}

$("#continue").on("click", function(e) {
    $(location).attr('href', survey_url)
});

function convert_form_to_text(user_utterance) {
    // Add new row for user-utterance
    user_row = $('<tr><td style="width:10%">YOU:</td><td style="width:90%">' + user_utterance + '</td></tr>');
    $("#form-row").before(user_row);
    // Clear input box
    $("#input-box").val('')
}

function poor_utterance(utterance) {
    if (utterance == trigger_channel_id || utterance == action_channel_id) {
        return false;
    } else {
        var re = /^([a-zA-Z0-9-]*\_)+([a-zA-Z0-9-]*)$/;
        return re.test(utterance);
    }

}

function change_color_using_intent(intent) {
    paragraphs = $(".right").find("p");

    if (intent == "confirm" || intent == "reword") {
        return;
    }

    paragraphs.each(function() {
        $(this).css('color', 'black')
    })

    if(intent == "trigger_function") {
        $(paragraphs[1]).css('color', 'red');
    } else if(intent == "trigger_channel") {
        $(paragraphs[2]).css('color', 'red');
    } if(intent == "action_function") {
        $(paragraphs[3]).css('color', 'red');
    } if(intent == "action_channel") {
        $(paragraphs[4]).css('color', 'red');
    }
}