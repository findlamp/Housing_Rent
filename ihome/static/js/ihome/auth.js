function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // Query the user's real-name authentication information
    $.get("/api/v1.0/users/auth", function(resp){
        // 4101 represents that User not logged in
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        } else if ("0" == resp.errno) {
            // If real_name and id_card are not null，it will represent that User has real name authentication.
            if (resp.data.real_name && resp.data.id_card) {
                $("#real-name").val(resp.data.real_name);
                $("#id-card").val(resp.data.id_card);
                // Add a disabled property to the input to prevent the user from modifying it
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                // Hide the submit save button
                $("#form-auth>input[type=submit]").hide();
            }
        } else {
            alert(resp.errmsg);
        }
    }, "json");

    // Manages the submission behavior of the real-name information form
    $("#form-auth").submit(function(e){
        e.preventDefault();
        // Display an error message if the user did not complete the form
        var realName = $("#real-name").val();
        var idCard = $("#id-card").val();
        if (realName == "" ||  idCard == "") {
            $(".error-msg").show();
        }

        // Converts the form's data to a JSON string
        var data = {
            real_name: realName,
            id_card: idCard
        };
        var jsonData = JSON.stringify(data);

        // Send a request to the back end
        $.ajax({
            url:"/api/v1.0/users/auth",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFTOKEN": getCookie("csrf_token")
            },
            success: function (resp) {
                if (0 == resp.errno) {
                    $(".error-msg").hide();
                    // Display a successful save message
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();
                }
            }
        });
    })

})