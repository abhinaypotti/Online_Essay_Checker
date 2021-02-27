/*name();
function name() {
    var email = document.getElementById('email').value;
    document.getElementById('email_profile').innerHTML = email;
}*/

currone=null
function downloadfile(){
    var fso = CreateObject("Scripting.FileSystemObject"); 
var a = fso.CreateTextFile("~/Downloads/testfile.txt", true);
a.WriteLine(document.getElementById('tarea').innerHTML);
a.Close();
}

function findlink(obj){
    if(currone!=null)
        currone.setAttribute('style','background-color:#5a6268');
    t=obj.innerHTML;
    p=document.getElementById('tarea').value;
    console.log(p);
    data={'keyword':t,'para':p};
    $.get('synlink',data,function(rdata,status){
        console.log(rdata);
        linklist=rdata['Result']['links'];
        synlist=rdata['Result']['synonyms'];
        currone=obj;
        obj.setAttribute('style','background-color:green');
        displink(linklist);
        dispsyn(synlist);
    });

}

function displink(llist){
    var linklist=document.getElementById('demo2');
    var child = linklist.lastElementChild;  
        while (child) { 
            linklist.removeChild(child); 
            child = linklist.lastElementChild; 
        } 
    for(var i=0;i<llist.length;i++)
    {
        var li = document.createElement('li');     // create li element.
        li.innerHTML = '<a href="'+llist[i]+'">'+llist[i]+'</a>';      // assigning text to li using array value.
        li.setAttribute('style', 'display: block;color:white;'); 
        linklist.appendChild(li); 
    }
}

function dispsyn(slist){
    var synlist=document.getElementById('demo3');
    var child = synlist.lastElementChild;  
        while (child) { 
            synlist.removeChild(child); 
            child = synlist.lastElementChild; 
        } 
    for(var i=0;i<slist.length;i++)
    {
        var li = document.createElement('li');     // create li element.
        li.innerHTML = slist[i];      // assigning text to li using array value.
        li.setAttribute('style', 'display: block;color:white;'); 
        console.log(slist[i]);
        synlist.appendChild(li); 
    }
}