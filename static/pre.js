
$('select').change(function(){
   var index = $('option:selected',this).index()-1;
    var table = document.getElementById("myTable").getElementsByTagName('tbody')[0]

  rows = "";
  for (i = 0 ; i < prerequsets[index].length ; i++){
    rows += '<tr><td>' + (i+1) + '</td><td>' + prerequsets[index][i] + '</td> </tr>';


  }
  table.innerHTML = rows
});
