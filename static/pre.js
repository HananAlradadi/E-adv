
$('select').change(function(){
   var index = $('option:selected',this).index()-1;
    var table = document.getElementById("myTable");

  for (i = table.rows.length-1 ; i >= 1  ; i-- ){
     table.deleteRow(i);
  }
  for (i = 0 ; i < prerequsets[index].length ; i++){
    var row = table.insertRow(i+1);
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  cell1.innerHTML = i+1;
  cell2.innerHTML = prerequsets[index][i] ;

  }






});