$(document).ready(function() {
    /* we don't want our menu headings firing off, so catch and kill them here */
    $('a[data-target]').click(function(e){
        if (e.which == 1) {
            event.preventDefault();
        }    
    })
})