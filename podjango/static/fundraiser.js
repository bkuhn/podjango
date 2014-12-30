/* Copyright (C) 2012-2013 Denver Gingerich, 
** Copyright (C) 2013-2014 Bradley M. Kuhn.
** License: GPLv3-or-later
**  Find a copy of GPL at https://sfconservancy.org/GPLv3
*/

$(document).ready(function() {
    var goal  = $('span#fundraiser-goal').text();
    var soFar = $('span#fundraiser-so-far').text();
    var noCommaGoal = goal.replace(/,/g, "");
    var noCommaSoFar = soFar.replace(/,/g, "");
    var percentage = (parseFloat(noCommaSoFar) / parseFloat(noCommaGoal)) * 100;

    $('span#fundraiser-percentage').text(percentage.toFixed(2) + "%");
    $("#progressbar").progressbar({ value:  percentage });
});
    
