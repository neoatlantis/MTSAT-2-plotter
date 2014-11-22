$(function(){
//////////////////////////////////////////////////////////////////////////////

/* Date concerning functions */

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

function compareDate(a, b){ // if a<=b
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


/* Retrive index file (log.txt) and auto parse */
var indexFileCache = {}, dateFileMetadata = {};
function loadIndexFile(dateMonth, callback){
    function parser(s){
        var sp = s.split('\n'), lp, range, filename, filenameS;
        for(var i in sp){
            if(!sp[i]) continue;
            lp = sp[i].trim().split('\t');
            range = lp[2].trim().slice(1,-1).split(',');
            filename = lp[0].trim();
            filenameS = filename.split('.');
            dateFileMetadata[filename] = {
                'time': filenameS[0],
                'date': filenameS[0].slice(0, 8),
                'dateMonth': filenameS[0].slice(0, 6),
                'channel': filenameS[1],
                'south': 'FULL' == filenameS[2] || 'SOUTH' == filenameS[2],
                'north': 'FULL' == filenameS[2] || 'NORTH' == filenameS[2],
                'range': {
                    x1: range[0],
                    y1: range[1],
                    x2: range[2],
                    y2: range[3],
                }
            };
        };
    };
    if(undefined !== indexFileCache[dateMonth]){
        parser(indexFileCache[dateMonth]);
        callback();
    } else {
        $.get(
            'http://mtsat-2.neoatlantis.org/data/' + dateMonth + '/log.txt',
            function(s){
                indexFileCache[dateMonth] = s;
                parser(s);
                callback();
            }
        );
    };
};

//////////////////////////////////////////////////////////////////////////////

/* filter date list */

var dateFilterStart, dateFilterEnd;
function filterDateList(){
    // the filter updates the list in UI by given start and end.  date list
    // being filtered(`dateFileMetadata`) is maintained by 'loadIndexFile'
    // function.
    
    for(var filename in dateFileMetadata){
        var metadata = dateFileMetadata[filename];
        $('body').append(JSON.stringify(metadata));
    };
};


/* initialize interface */

function validateDateRange(){
    var viewDateRangeStart = $('[name="view-date-range-start"]').val(),
        viewDateRangeEnd = $('[name="view-date-range-end"]').val();

    // if validation passed, they will be numbers taken apart [YYYY, MM, DD]
    var dateRangeStart = validateDateFormat(viewDateRangeStart),
        dateRangeEnd = validateDateFormat(viewDateRangeEnd);
    
    if(false === dateRangeStart || false === dateRangeEnd)
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

    // [[YYYY, MM, DD], [YYYY, MM, DD], 'YYYYMMDD', 'YYYYMMDD']
    return [dateRangeStart, dateRangeEnd, viewDateRangeStart, viewDateRangeEnd];
};


$('#choose-date-range').click(function(){
    var dateRange = validateDateRange();
    if(false === dateRange)
        return alert('输入的日期范围有误。起始日期必须早于终止日期，且不早于2014年11月19日; 终止日期不得晚于今日。');

    var year = dateRange[0][0], month = dateRange[0][1];

    // set date filter range
    dateFilterStart = dateRange[2]; // str
    dateFilterEnd = dateRange[3]; // str

    function toDateMonth(year, month){
        return String(year) + ((month < 10)?('0' + String(month)):String(month));
    };
    var list = [toDateMonth(year, month)];
    while(year != dateRange[1][0] && month != dateRange[1][1]){
        month += 1;
        if(month > 12){
            month = 1;
            year += 1;
        };
        list.push(toDateMonth(year, month));
    };

    for(var i=0; i<list.length; i++)
        loadIndexFile(list[i], filterDateList);
});

//////////////////////////////////////////////////////////////////////////////
});
