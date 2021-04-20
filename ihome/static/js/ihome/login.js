function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("Please enter the right phone number！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("Please enter the password!");
            $("#password-err").show();
            return;
        }
        // Preserve the data in the object
        var data = {
            mobile: mobile,
            password: passwd
        };
        // Convert data to a JSON string
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/sessions",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (data) {
                if (data.errno == "0") {
                    // login success, back to homepage
                    location.href = "/";
                }
                else {
                    // error information
                    $("#password-err span").html(data.errmsg);
                    $("#password-err").show();
                }
            }
        });
    });
})