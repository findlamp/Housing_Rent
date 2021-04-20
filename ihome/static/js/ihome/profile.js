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


$(document).ready(function () {
    $("#form-avatar").submit(function (e) {
        // Prevents the default behavior of the form
        e.preventDefault();
        // Use AjaxSubmit provided by jQuery.form.min.js to submit the form asynchronously
        $(this).ajaxSubmit({
            url: "/api/v1.0/users/avatar",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // submit success
                    var avatarUrl = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatarUrl);
                } else if (resp.errno == "4101") {
                    location.href = "/login.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });

    // The back end of the page load is queried for user information
    $.get("/api/v1.0/user", function(resp){
        // User not logged in
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        }
        // get the user information
        else if ("0" == resp.errno) {
            $("#user-name").val(resp.data.name);
            if (resp.data.avatar) {
                $("#user-avatar").attr("src", resp.data.avatar);
            }
        }
    }, "json");

     $("#form-name").submit(function(e){
        e.preventDefault();
        // get parameters
        var name = $("#user-name").val();

        if (!name) {
            alert("Please enter the username！");
            return;
        }
        $.ajax({
            url:"/api/v1.0/users/name",
            type:"PUT",
            data: JSON.stringify({name: name}),
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                } else if ("4001" == data.errno) {
                    $(".error-msg").show();
                } else if ("4101" == data.errno) {
                    location.href = "/login.html";
                }
            }
        });
    })
})
