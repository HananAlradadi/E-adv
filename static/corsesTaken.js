
    if (cru.length > 0){
        Table = document.getElementById("myTable1")
        for(i = 0 ; i < cru.length ; i++ ){
      row = Table.insertRow(-1);
      indexs = Table.rows.length-1
      row.innerHTML = '<td>'+indexs+'</td><td>'+cru[i]+'</td><td><button id = "'+indexs+'" onclick="deleteRowbyIndex(this.id)" type="button" class="btn btn-danger">حذف</button></td></tr>'
          CN = document.getElementById('CN')
    CN.value = CN.value+""+ cru[i]+","
    }
    }
    function addRow(){
      ifinList = true
      Table = document.getElementById("myTable1")
      cols = Table.querySelectorAll("td:nth-child(2)");      
      selects = document.getElementsByTagName('select')[0]
      CoursesName = selects.options[selects.selectedIndex]
      if (CoursesName.text == "المقرر") {
        document.getElementsByTagName('p')[0].innerHTML = 'يجب اختيار مقرر'
      }
      else{

      sum = 0 ;
      for(i=0 ; i < cols.length ; i++){
      if (cols[i].textContent == CoursesName.text ){
document.getElementsByTagName('p')[0].innerHTML = 'تم اضافة المقرر سابقا'
ifinList = false  
break

            

}
      }
      

      if (ifinList){

      for(i=0 ; i < cols.length ; i++){
        for(j=0 ; j < courses.length ; j++){
          
          if (cols[i].textContent == courses[j][0] ){

            sum += courses[j][1]

}
if (CoursesName.text == courses[j][0] && i == 0 ){

sum += courses[j][1]


}

      }
    }
      if(sum <= maxCR){


      row = Table.insertRow(-1);

      indexs = Table.rows.length-1 
      row.innerHTML = '<td>'+indexs+'</td><td>'+CoursesName.text+'</td><td><button id = "'+indexs+'" onclick="deleteRowbyIndex(this.id)" type="button" class="btn btn-danger">حذف</button></td></tr>'
          CN = document.getElementById('CN') 
    CN.value = CN.value+""+ CoursesName.text+","
          document.getElementsByTagName('p')[0].innerHTML = ''
}
      else{
        document.getElementsByTagName('p')[0].innerHTML = 'لا يمكن اضافة المقرر لتجاوز النصاب'
      }
    }
    }
  }

    function deleteRowbyIndex(index) { 
      Table = document.getElementById("myTable1")
      Table.deleteRow(index);
    cols = Table.querySelectorAll("td:first-child");
    buttonIDs = Table.getElementsByTagName('button')
    for(i=0 ; i < cols.length ; i++){

      cols[i].innerHTML = ''+(i+1)
    }
    for(i=0 ; i < buttonIDs.length ; i++){

      buttonIDs[i].id = ''+(i+1)
}
CN = document.getElementById('CN') 
    CN.value = ""
    trs = Table.getElementsByTagName('tr') 
    for(i = 1 ; i< trs.length ; i++){
      CN.value += trs[i].getElementsByTagName('td')[1].innerHTML +","
      
    }
    }
function check(){
      if( document.getElementById("myTable1").rows.length > 1)
       { 
        return true
        
       }
      else{
        document.getElementsByTagName('p')[0].innerHTML = ' يجب اختيار مقرر او اكثر'
       return false
      }
    }