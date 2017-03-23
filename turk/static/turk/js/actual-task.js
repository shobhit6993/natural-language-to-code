$("#continue").hide()
var count = 16;
var counter=setInterval(timer, 1000); //1000 will  run it every 1 second

function timer() {
    count = count - 1;
    if (count <= 0)
    {
        clearInterval(counter);
        document.getElementById("timer").innerHTML = "";
        $("#continue").show()
        return;
    }
    document.getElementById("timer").innerHTML = "Spend some time in understanding the task; the \"Continue\" button will appear in " + count + " seconds.";
}

$("#continue").on("click", function(e) {
    $(location).attr('href', actual_conversation_url)
});
