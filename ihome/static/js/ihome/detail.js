function hrefBack() {
    history.go(-1);
}

// Parse the query string parameters in the extract URL
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // Get the house id
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // Get the house information
    $.get("/api/v1.0/houses/" + houseId, function(resp){
        if ("0" == resp.errno) {
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:resp.data.house.img_urls, price:resp.data.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:resp.data.house}));

            // resp.user_id for user,resp.data.user_id for landlord
            if (resp.data.user_id != resp.data.house.user_id) {
                $(".book-house").attr("href", "/booking.html?hid="+resp.data.house.hid);
                $(".book-house").show();
            }
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            });
        }
    })
})