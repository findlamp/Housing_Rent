$(document).ready(function(){
    // For the release of housing, only the user after authentication can, so judge the user's real-name authentication status first
    $.get("/api/v1.0/users/auth", function(resp){
        if ("4101" == resp.errno) {
            // User not logged in
            location.href = "/login.html";
        } else if ("0" == resp.errno) {
            // unauthenticated users
            if (!(resp.data.real_name && resp.data.id_card)) {
                $(".auth-warn").show();
                return;
            }
            // authenticated users
            $.get("/api/v1.0/user/houses", function(resp){
                if ("0" == resp.errno) {
                    $("#houses-list").html(template("houses-list-tmpl", {houses:resp.data.houses}));
                } else {
                    $("#houses-list").html(template("houses-list-tmpl", {houses:[]}));
                }
            });
        }
    });
})