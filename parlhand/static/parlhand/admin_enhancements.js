var editor1;
var editor2;
var make_called = 0;
function makeEditors() {
    make_called++;
    var area = $('.item-wrapper-datatablecontent div.scripts')[0]
    console.log(area,'thing')
    if (area != undefined && editor1 == undefined) {
        var ed1ta = $('.item-wrapper-datatablecontent .scripts textarea');
        ed1 = $('<div id="code-editor-1" style="height:500px"></div>').appendTo('.item-wrapper-datatablecontent div.scripts');
        ed1ta.hide();

        editor1 = ace.edit("code-editor-1");
        //editor1.setTheme("ace/theme/monokai");
        //editor1.getSession().setMode("ace/mode/javascript");
        editor1.getSession().setValue(ed1ta.val());
        editor1.getSession().on('change', function(e) {
            ed1ta.val(editor1.getValue())
        });
    
        var ed2ta = $('.item-wrapper-datatablecontent .script textarea');
        ed2 = $('<div id="code-editor-2" style="height:500px"></div>').appendTo('.item-wrapper-datatablecontent div.script');
        ed2ta.hide();

        editor2 = ace.edit("code-editor-2");
        //editor2.setTheme("ace/theme/monokai");
        //editor2.getSession().setMode("ace/mode/javascript");
        editor2.getSession().setValue(ed2ta.val());
        editor2.getSession().on('change', function(e) {
            ed2ta.val(editor2.getValue())
        });
        
    }
    if (editor1 == undefined) {
        console.log('tried and failed')
        if (make_called < 5 ) {
            setTimeout(makeEditors,2000)
        }
    }
}

document.addEventListener('DOMContentLoaded', makeEditors, false);
