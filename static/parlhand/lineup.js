function make_sortable(id,parent_id) {
    var elem = document.getElementById(id);
    Sortable.create(elem, {
        group: { name: "sortables", pull: 'clone' },
        handle: ".handle",
        draggable: ".draggable_block",
        animation: 200,
        onAdd: function (evt) {
            var itemEl = evt.item;  // dragged HTMLElement
            input = itemEl.getElementsByTagName('input')[0]
            input.setAttribute('name',parent_id)
        },
    });
}

$(document).ready(function() {
    $('.lineup_text').on('input',function(e){
        this.title=this.value;
    });
})