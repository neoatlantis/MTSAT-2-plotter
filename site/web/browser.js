$(function(){
//////////////////////////////////////////////////////////////////////////////

function validateDateFormat(s){
    if(!/^[0-9]{8}$/.test(s)) return false;
    var year = parseInt(s.slice(0,4), 10),
        month = parseInt(s.slice(4,6), 10),
        day = parseInt(s.slice(6, 8));
    if(year < 2014) return false;
    if(month < 1 || month > 12) return false;
    if(day < 1) return false;

    var dayMax = 0;
    if(2 == month){
        if( ((0 == year % 100)?(0 == year % 400):(0 == year % 4)) )
            // is leap year
            dayMax = 29;
        else
            dayMax = 28;
    } else {
        if(month <= 7)
            dayMax = ((1 == month % 2)?31:30);
        else
            dayMax = ((1 == month % 2)?30:31);
    };
    if(day > dayMax) return false;
    return [year, month, day]; 
};

function compareDate(a, b){ // if a<b
    var year1 = parseInt(a.slice(0,4), 10),
        month1 = parseInt(a.slice(4,6), 10),
        day1 = parseInt(a.slice(6, 8));
    var year2 = parseInt(b.slice(0,4), 10),
        month2 = parseInt(b.slice(4,6), 10),
        day2 = parseInt(b.slice(6, 8));

    var aBigger = false;
    if(year1 > year2)
        aBigger = true;
    else if (year1 == year2)
        if(month1 > month2)
            aBigger = true;
        else if(month1 == month2)
            if(day1 > day2)
                aBigger = true;

    return !aBigger;
};

/* Get satellite image from given filename */
var loadDataCache = {}
var loadData = function(filename, callback){
    if(!/^[0-9]{12}\.((IR[1-4])|VIS)\.(FULL|NORTH|SOUTH)\.png$/.test(filename))
        return false;

    var datemonth = filename.slice(0, 6),
        url = 'http://mtsat-2.neoatlantis.org/data/'
            + datemonth
            + '/' + filename
    ;

    if(undefined !== loadDataCache[filename]){
        callback(img);        
    } else {
        var img = new Image();
        img.src = url;
        img.onload = function(){
            if(
                !this.complete ||
                typeof this.naturalWidth == "undefined" ||
                this.naturalWidth == 0
            )
                loadDataCache[filename] = false;
            else
                loadDataCache[filename] = img;
            callback(loadDataCache[filename]);
        };
    };
};



/* initialize interface */

function validateDateRange(){
    var viewDateRangeStart = $('[name="view-date-range-start"]').val(),
        viewDateRangeEnd = $('[name="view-date-range-end"]').val();
    
    if(
        false === validateDateFormat(viewDateRangeStart) ||
        false === validateDateFormat(viewDateRangeEnd)
    )
        return false;

    if(!compareDate(viewDateRangeStart, viewDateRangeEnd))
        return false;

    if(!compareDate('20141119', viewDateRangeStart))
        return false;

    var nowtime = new Date(), nowtimeStr = '', nowtimeY, nowtimeM, nowtimeD;
    nowtimeY = nowtime.getUTCFullYear();
    nowtimeM = nowtime.getUTCMonth() + 1;
    nowtimeD = nowtime.getUTCDate();
    
    nowtimeStr = String(nowtimeY);
    if(nowtimeM < 10) nowtimeStr += '0';
    nowtimeStr += String(nowtimeM);
    if(nowtimeD < 10) nowtimeStr += '0';
    nowtimeStr += String(nowtimeD);

    if(!compareDate(viewDateRangeEnd, nowtimeStr))
        return false;

    return true;
};

$('#choose-date-range').click(function(){
    if(false === validateDateRange())
        return alert('输入的日期范围有误。');
});

//////////////////////////////////////////////////////////////////////////////
});
