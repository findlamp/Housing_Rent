// Js reads cookie
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
/*
// 
var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // Form the image CAPTCHAs back-end address, set to the page, let the browser request CAPTCHAs image
    // 1. Generate image verification code number
    imageCodeId = generateUUID();
    // picture url
    var url = "/api/v1.0/image_codes/" + imageCodeId;
    $(".image-code img").attr("src", url);
}

function sendSMSCode() {
    // The function to be executed after clicking Send SMS Captcha
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("Please enter the right phone number！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("Please enter the verification code！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // Construct the parameters of the backend request
    var req_data = {
        image_code: imageCode, // picture verification code 
        image_code_id: imageCodeId // picture verification code id
    };

    // Send a request to the back end
    
    $.get("/api/v1.0/sms_codes/"+ mobile, req_data, function (resp) {
        //Resp is the response value returned by the back end, because the back end returns a JSON string,
        // So Ajax helps you convert this JSON string into a JS object, and the RESP is the converted object
        if (resp.errno == "0") {
            var num = 60;
            // submit success
            var timer = setInterval(function () {
                if (num >= 1) {
                    // Modify the text
                    $(".phonecode-a").html(num + "秒");
                    num -= 1;
                } else {
                    $(".phonecode-a").html("Get the erification code");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer);
                }
            }, 1000, 60)
        } else {
            alert(resp.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        }
    });
}
*/

$(document).ready(function() {
    //generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    /*
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    */
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });


   
    $(".form-register").submit(function(e){
        // Prevents the browser's default auto-submit behavior for forms
        e.preventDefault();

        var mobile = $("#mobile").val();
        //var phoneCode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("Please enter the right phone number！");
            $("#mobile-err").show();
            return;
        } 
        /*
        if (!phoneCode) {
            $("#phone-code-err span").html("Please enter the text verification code！");
            $("#phone-code-err").show();
            return;
        }
        */
        if (!passwd) {
            $("#password-err span").html("Please enter the password!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("can't match!");
            $("#password2-err").show();
            return;
        }

        // Invoking Ajax sends a registration request to the back end
        var req_data = {
            mobile: mobile,
            //sms_code: phoneCode,
            password: passwd,
            password2: passwd2,
        };
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url: "/api/v1.0/users",
            type: "post",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, 
            success: function (resp) {
                if (resp.errno == "0") {
                    // signup success
                    location.href = "/index.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        })

    });
})