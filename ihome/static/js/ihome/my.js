function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// execute when the push button is clicked
function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if ("0" == resp.errno) {
                location.href = "/index.html";
            }
        }
    });
}

$(document).ready(function(){
    $.get("/api/v1.0/user", function(resp){
        // User not logged in
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        }
        // get the user information
        else if ("0" == resp.errno) {
            $("#user-name").html(resp.data.name);
            $("#user-mobile").html(resp.data.mobile);
            if (resp.data.avatar) {
                $("#user-avatar").attr("src", resp.data.avatar);
            }

        }
    }, "json");
})