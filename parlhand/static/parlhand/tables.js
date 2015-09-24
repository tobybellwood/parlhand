var val_lookup = {};
function valsorter(a,b) {
    // This is kind of inefficient, maybe we should look at helping improve the js library.
    if (val_lookup[a]) {
        a = val_lookup[a];
    } else {
        val_lookup[a] = $('td').filter(function(){ return $(this).html() == a; }).data('value');
        a = val_lookup[a];
    }
    if (val_lookup[b]) {
        b = val_lookup[b];
    } else {
        val_lookup[b] = $('td').filter(function(){ return $(this).html() == b; }).data('value');
        b = val_lookup[b];
    }
    if (a > b) return 1;
    if (a < b) return -1;
    return 0;
}