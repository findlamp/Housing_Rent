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
    // Check the landlord's order
    $.get("/api/v1.0/user/orders?role=landlord", function(resp){
        if ("0" == resp.errno) {
            $(".orders-list").html(template("orders-list-tmpl", {orders:resp.data.orders}));
            $(".order-accept").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-accept").attr("order-id", orderId);
            });
            // accept order
            $(".modal-accept").on("click", function(){
                var orderId = $(this).attr("order-id");
                $.ajax({
                    url:"/api/v1.0/orders/"+orderId+"/status",
                    type:"PUT",
                    data:'{"action":"accept"}',
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
                            $("#accept-modal").modal("hide");
                        }
                    }
                })
            });
            $(".order-reject").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });
            // deny order
            $(".modal-reject").on("click", function(){
                var orderId = $(this).attr("order-id");
                var reject_reason = $("#reject-reason").val();
                if (!reject_reason) return;
                var data = {
                    action: "reject",
                    reason:reject_reason
                };
                $.ajax({
                    url:"/api/v1.0/orders/"+orderId+"/status",
                    type:"PUT",
                    data:JSON.stringify(data),
                    contentType:"application/json",
                    headers: {
                        "X-CSRFTOKEN":getCookie("csrf_token")
                    },
                    dataType:"json",
                    success:function (resp) {
                        if ("4101" == resp.errno) {
                            location.href = "/login.html";
                        } else if ("0" == resp.errno) {
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("Denied");
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            $("#reject-modal").modal("hide");
                        }
                    }
                });
            })
        }
    });
});