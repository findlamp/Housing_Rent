//Modal frame center control
function centerModals(){
    $('.modal').each(function(i){   //Iterate each modal box
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //Modify
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //modal box appear
    $(window).on('resize', centerModals);
    // get the order
    $.get("/api/v1.0/user/orders?role=custom", function(resp){
        if ("0" == resp.errno) {
            $(".orders-list").html(template("orders-list-tmpl", {orders:resp.data.orders}));
            $(".order-pay").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $.ajax({
                    url: "/api/v1.0/orders/" + orderId + "/payment",
                    type: "get",
                    dataType: "json",
                    headers: {
                        "X-CSRFToken": getCookie("csrf_token"),
                    },
                    success: function (resp) {
                       
                        //location.href = "/payComplete.html"
                        
                        if ("4101" == resp.errno) {
                            location.href = "login.html";
                        } else if ("0" == resp.errno) {
                            
                            location.href = resp.data.pay_url
                        }
                        
                    }
                });
            });
            $(".order-comment").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-comment").attr("order-id", orderId);
            });
            $(".modal-comment").on("click", function(){
                var orderId = $(this).attr("order-id");
                var comment = $("#comment").val()
                if (!comment) return;
                var data = {
                    order_id:orderId,
                    comment:comment
                };
                // deal with comment
                $.ajax({
                    url:"/api/v1.0/orders/"+orderId+"/comment",
                    type:"PUT",
                    data:JSON.stringify(data),
                    contentType:"application/json",
                    dataType:"json",
                    headers:{
                        "X-CSRFTOKEN":getCookie("csrf_token"),
                    },
                    success:function (resp) {
                        if ("4101" == resp.errno) {
                            location.href = "/login.html";
                        } else if ("0" == resp.errno) {
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("Accepted");
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            $("#comment-modal").modal("hide");
                        }
                    }
                });
            });
        }
    });


});