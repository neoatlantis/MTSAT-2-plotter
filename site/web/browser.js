$(function(){
//////////////////////////////////////////////////////////////////////////////

function validateDateFormat(s){
    if(!/^[0-9]{8}$/.test(s)) return false;
    var year = parseInt(s.slice(0,4), 10),
        month = parseInt(s.slice(4,6), 10),
        day = parseInt(s.slice(6, 8));
    if(year < 2014) return false;
    if(month < 1 or month > 12) return false;
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





/* initialize interface */

function validateDateRange(){
    var viewDateRangeStart = $('[name="view-date-range-start"]').text(),
        viewDateRangeEnd = $('[name="view-date-range-end"]').text();
    
    if(!(
        validateDateFormat(viewDateRangeStart) && 
        validateDateFormat(viewDateRangeEnd))
    )
        return false;
    
};

//////////////////////////////////////////////////////////////////////////////
});
