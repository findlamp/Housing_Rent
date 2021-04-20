var cur_page = 1; // current page
var next_page = 1; // next page
var total_page = 1;  // total page
var house_data_querying = true;   // Whether fetch data from the background

// Parse the query string in the URL
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

// Update the filter selected by the user
function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("Check-in Date");
    }
}


// Update listing information
// Action represents how data requested from the back end is displayed on the front end
// Append mode is adopted by default
// action=renew 
function updateHouseData(action) {
    var areaId = $(".filter-area>li.active").attr("area-id");
    if (undefined == areaId) areaId = "";
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var sortKey = $(".filter-sort>li.active").attr("sort-key");
    var params = {
        aid:areaId,
        sd:startDate,
        ed:endDate,
        sk:sortKey,
        p:next_page
    };
    $.get("/api/v1.0/houses", params, function(resp){
        house_data_querying = false;
        if ("0" == resp.errno) {
            if (0 == resp.data.total_page) {
                $(".house-list").html("The housing information that meets your query is not available at present.");
            } else {
                total_page = resp.data.total_page;
                if ("renew" == action) {
                    cur_page = 1;
                    $(".house-list").html(template("house-list-tmpl", {houses:resp.data.houses}));
                } else {
                    cur_page = next_page;
                    $(".house-list").append(template("house-list-tmpl", {houses: resp.data.houses}));
                }
            }
        }
    })
}

$(document).ready(function(){
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate);
    $("#end-date").val(endDate);
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    if (!areaName) areaName = "Location";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);


    //Gets the city area information
    $.get("/api/v1.0/areas", function(data){
        if ("0" == data.errno) {
            // The user may have selected the city when jumping from the home page to the search page
            //so try to extract the city selected by the user from the query string parameter of the URL
            var areaId = queryData["aid"];
            // extract city ID
            if (areaId) {
                // Iterate through the urban area information obtained from the back end and add it to the page
                for (var i=0; i<data.data.length; i++) {
                    areaId = parseInt(areaId);
                    if (data.data[i].aid == areaId) {
                        $(".filter-area").append('<li area-id="'+ data.data[i].aid+'" class="active">'+ data.data[i].aname+'</li>');
                    } else {
                        $(".filter-area").append('<li area-id="'+ data.data[i].aid+'">'+ data.data[i].aname+'</li>');
                    }
                }
            } else {
                // If there is no city information in the URL parameter, no additional processing is needed and it is displayed directly in the page
                for (var i=0; i<data.data.length; i++) {
                    $(".filter-area").append('<li area-id="'+ data.data[i].aid+'">'+ data.data[i].aname+'</li>');
                }
            }
            // update the display listing information after you add the Good City option information to the page
            updateHouseData("renew");
            // Get the height of the page display window
            var windowHeight = $(window).height();
            // Add event functions for window scrolling
            window.onscroll=function(){
                // var a = document.documentElement.scrollTop==0? document.body.clientHeight : document.documentElement.clientHeight;
                var b = document.documentElement.scrollTop==0? document.body.scrollTop : document.documentElement.scrollTop;
                var c = document.documentElement.scrollTop==0? document.body.scrollHeight : document.documentElement.scrollHeight;
                // scroll down to near the bottom of the window
                if(c-b<windowHeight+50){
                    if (!house_data_querying) {
                        house_data_querying = true;
                        if(cur_page < total_page) {
                            next_page = cur_page + 1;
                            updateHouseData();
                        } else {
                            house_data_querying = false;
                        }
                    }
                }
            }
        }
    });

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function(e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        cur_page = 1;
        next_page = 1;
        total_page = 1;
        updateHouseData("renew");

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })
})