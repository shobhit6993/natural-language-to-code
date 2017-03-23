var message = "The above example should have given you an idea of how to converse with the bot. Press 'Continue' to move on to a real-time conversation with the bot in which you will describe a new task.";
var table = $("#conversation");
var form = $("#dialog-form");

table.hide();
form.hide();
$("#continue").hide();

$('#start').on('click', function(e) {
    $(this).hide();
    table.show();
    form.show();

    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">Hi! Please describe the applet you want to create for automating the task you have on your mind.</td></tr>');
    $("#form-row").before(robot_row);

    // Add options for user-utterance.
    form_buttons = '<label><input type="radio" name="user_utterance" value="free-form-correct"><span>save facebook photos to dropbox folder</span></label><br><label><input type="radio" name="user_utterance" value="incorrect"><span>save photos</span></label><br><input type="submit" id="submit" value="Send"><div id="error-message"></div>'
    form.append(form_buttons);
});

form.on('submit', function(e) {
    e.preventDefault();
    var form_data_serialized = form.serialize();
    var form_data = get_url_vars(form_data_serialized);
    if (!is_valid(form_data)) {
        $("#error-message").html("Please select a message.");
        return false;
    }
    else {
        $("#error-message").html("");
        utterance = form_data['user_utterance']
        if(utterance == "incorrect") {
            convert_form_to_text(false);
            reword();
        } else if (utterance == "free-form-correct") {
            convert_form_to_text(true);
            ask_trigger_fn()
        } else if (utterance == "trigger-fn-correct") {
            convert_form_to_text(true);
            confirm_trigger_fn()
        } else if (utterance == "trigger-fn-confirm") {
            convert_form_to_text(true);
            ask_action_channel()
        } else if (utterance == "action-channel-correct") {
            convert_form_to_text(true);
            inform()
        } else if (utterance == "inform") {
            convert_form_to_text(true);
            end_demonstration()
        }
        return false;
    }
});

$("#continue").on("click", function(e) {
    $(location).attr('href', actual_task_url)
});

function reword() {
    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">Sorry, I didn\'t get that. Could you please reword your previous message?</td></tr>');
    $("#form-row").before(robot_row);
}

function convert_form_to_text(clear_form) {
    var f = document.getElementById("dialog-form");
    var utterance = getText(f["user_utterance"]);

    if (clear_form) {
        form.empty();
    }

    // Add new row for user-utterance
    user_row = $('<tr><td style="width:10%">YOU:</td><td style="width:90%">' + utterance + '</td></tr>');
    $("#form-row").before(user_row);
}

function ask_trigger_fn() {
    // Highlight the relevant section in "Task Description."
    change_all_to_black();
    $($(".right").find("p")[2]).css('color', 'red');

    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">Which event on Facebook should I be looking for to run the applet?</td></tr>');
    $("#form-row").before(robot_row);

    // Add options for user-utterance.
    form_buttons = '<label><input type="radio" name="user_utterance" value="trigger-fn-correct"><span>when I upload photos</span></label><br><input type="radio" name="user_utterance" value="incorrect"><span>new_photo_post_by_you</span></label><br><label><input type="radio" name="user_utterance" value="incorrect"><span>post pix !!! <3 :P</span></label><br><input type="submit" id="submit" value="Send"><div id="error-message"></div>'
    form.append(form_buttons)
}

function confirm_trigger_fn() {
    // Highlight the relevant section in "Task Description."
    change_all_to_black();
    $($(".right").find("p")[2]).css('color', 'red');

    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">Do you want to trigger the applet every time you post a new photo on facebook?</td></tr>');
    $("#form-row").before(robot_row);

    // Add options for user-utterance.
    form_buttons = '<label><input type="radio" name="user_utterance" value="incorrect"><span>yo!</span></label><br><label><input type="radio" name="user_utterance" value="trigger-fn-confirm"><span>yes</span></label><br><label><input type="radio" name="user_utterance" value="incorrect"><span>yeaassss</span></label><br><input type="submit" id="submit" value="Send"><div id="error-message"></div>'
    form.append(form_buttons)
}

function ask_action_channel() {
    // Highlight the relevant section in "Task Description."
    change_all_to_black();
    $($(".right").find("p")[5]).css('color', 'red');

    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">Which service should I use to perform the desired action every time the applet runs?</td></tr>');
    $("#form-row").before(robot_row);

    // Add options for user-utterance.
    form_buttons = '<label><input type="radio" name="user_utterance" value="incorrect"><span>drop box.com</span></label><br><label><input type="radio" name="user_utterance" value="action-channel-correct"><span>dropbox</span></label><br><input type="submit" id="submit" value="Send"><div id="error-message"></div>'
    form.append(form_buttons)
}

function inform() {
    change_all_to_black();

    // Add a row for system-utterance.
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">The applet will trigger every time you post a new photo on facebook. It will use the Facebook service to look for this event. The action taken will be to download a file at a given url and add it to dropbox at the path you specify. This action will be performed using the Dropbox service. Is this what you wanted?</td></tr>');
    $("#form-row").before(robot_row);

    // Add options for user-utterance.
    form_buttons = '<label><input type="radio" name="user_utterance" value="inform"><span>yes</span></label><br><input type="submit" id="submit" value="Send"><div id="error-message"></div>'
    form.append(form_buttons)
}

function end_demonstration() {
    change_all_to_black();
    robot_row = $('<tr><td style="width:10%">ROBOT:</td><td style="width:90%">Ok, bye!</td></tr>');
    $("#form-row").before(robot_row);
    $("#form-row").remove();
    $("#continue").show();
    $("#message").html(message);
}

function is_valid(js) {
    return ('user_utterance' in js)
}

function getText(radioList) {
    if ("length" in radioList) {
        for(var i = 0; i < radioList.length; i++) {
            if(radioList[i].value === radioList.value) {
                return radioList[i].parentNode.textContent.trim();
            }
        }
    } else {
        return radioList.parentNode.textContent.trim();
    }
}

function change_all_to_black() {
    $(".right").find("p").each(function() {
        $(this).css('color', 'black')
    });
}
