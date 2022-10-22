$('input[type=radio]').click(function(){
 contentShow = $(this).val(); 
 if (contentShow == "الشعب الغير متعارضة"){
     ms = ' قد يتم لا اضافة احدى المقررات او جميعها نظرا لامتلاء' + ' الشعب قبل التمكن من اضافته'
  coursescanadd()
  coursesDataTable = coursesData
 }
 else if (contentShow == "الشعب المتعارضة"){
      ms = 'سيتم حذف المقررات المتعارضة  واضافة المقررات المختارة ولكن قد يتم امتلاء احد الشعب\n' +
         'لاحدى المقررات او جميعها قبل التمكن من اضافته\n'
  coursescannotadd()


  coursesDataTable = []
  for(i = 0 ; i < coursesDatanot.length ; i++){
      coursesDataTable.push(coursesDatanot[i][coursesDatanot[i].length-1])

  }
 }
});

 ms = ' قد يتم لا اضافة احدى المقررات او جميعها نظرا لامتلاء' + ' الشعب قبل التمكن من اضافته'
htmlcode = ''
coursescanadd()
  function coursescannotadd(){
    if (coursesDatanot.length  > 0) {
  table = document.getElementById('myTable')
  table.getElementsByTagName('thead')[0].innerHTML = '<tr><th scope="col"> # </th><th scope="col"> المقررات التي لا يمكن اضافتها بسبب وجود تعارض مع الجدول الدراسي</th><th scope="col"> الشعبة</th><th scope="col"> مواعيد المحاضرات</th> <th scope="col">استاذ المادة</th><th scope="col"> المقرر المتعارض مع الشعبة</th></tr>'
  table = table.getElementsByTagName('tbody')[0]
  table.innerHTML = ""
  rowspannum = 0
  i = 0 
  k = 1
  while ( i < coursesDatanot.length ){
    row = table.insertRow(table.rows.length)   
    coll0 = row.insertCell()
    coll0.innerHTML = k
    coll1 = row.insertCell()
    coll1.innerHTML = coursesDatanot[i][coursesDatanot[i].length-1][2]
    time = ''
    for( h = 5 ; h <= 9 ; h++){
      if(coursesDatanot[i][coursesDatanot[i].length-1][h] != '-'){

        time = time + columnsDatanot[h]+ ": " + coursesDatanot[i][coursesDatanot[i].length-1][h] + " "
      }
    }
    row.insertCell().innerHTML = '<div class="form-check"><input onclick = "coursesDatanotValueCH()" class="form-check-input" type="checkbox" value="'+coursesDatanot[i][coursesDatanot[i].length-1][2]+'" id="'+coursesDatanot[i][coursesDatanot[i].length-1][3] +'"><label class="form-check-label" for="flexCheckDefault">'+ coursesDatanot[i][coursesDatanot[i].length-1][3] + '</label></div>'
    row.insertCell().innerHTML = time
    row.insertCell().innerHTML = coursesDatanot[i][coursesDatanot[i].length-1][4] 
    crnot = coursesDatanot[i][0][2]
    for(m = 1 ; m < coursesDatanot[i].length-1 ; m++){
      crnot += ','+coursesDatanot[i][m][2]
    }
    row.insertCell().innerHTML = crnot
    
    rowspannum = 1

    while (i+1 < coursesDatanot.length && coursesDatanot[i+1][coursesDatanot[i+1].length-1][2] == coursesDatanot[i][coursesDatanot[i].length-1][2]  ){
       row1 = table.insertRow(table.rows.length)

      time = ''
    for( h = 5 ; h <= 9 ; h++){
      if(coursesDatanot[i+1][coursesDatanot[i+1].length-1][h] != '-'){

        time = time + columnsDatanot[h]+ ": " + coursesDatanot[i+1][coursesDatanot[i+1].length-1][h] + " "
      }
    }
    row1.insertCell(-1).innerHTML = '<div class="form-check"><input onclick = "coursesDatanotValueCH()" class="form-check-input" type="checkbox" value="'+coursesDatanot[i+1][coursesDatanot[i+1].length-1][2]+'" id="'+coursesDatanot[i+1][coursesDatanot[i+1].length-1][3] +'"><label class="form-check-label" for="flexCheckDefault">'+ coursesDatanot[i+1][coursesDatanot[i+1].length-1][3] + '</label></div>'
    row1.insertCell(-1).innerHTML = time
    row1.insertCell(-1).innerHTML = coursesDatanot[i+1][coursesDatanot[i+1].length-1][4] 
    crnot = coursesDatanot[i+1][0][2]
    for(m = 1 ; m < coursesDatanot[i+1].length-1 ; m++){
      crnot += ','+coursesDatanot[i+1][m][2]
    }
    row1.insertCell(-1).innerHTML = crnot
     

      rowspannum++   
       

    i++
  }
  
  if (rowspannum > 1){
    
  coll0.rowSpan = rowspannum
  coll1.rowSpan = rowspannum  
  }
  //vertical-align: middle;
  coll0.style.cssText = 'vertical-align: middle'
  coll1.style.cssText = 'vertical-align: middle'
    i++
    k++
    //row.insertCell(j).innerHTML 
  }
  if (htmlcode != ''){
      document.getElementById('but').innerHTML = htmlcode
}
  document.getElementById('ms1').innerText = ms
        if (!avlAddDreap){

    document.getElementById('add').setAttribute("disabled", "disabled")
}
    }
    else{
              htmlcode = document.getElementById('but').innerHTML
         document.getElementById('but').innerHTML = ''
      document.getElementById('re').innerText = mes1
      table = document.getElementById('myTable')
  table.getElementsByTagName('thead')[0].innerHTML = ''
  table.getElementsByTagName('tbody')[0].innerHTML = ''



    }

  }
  
  
function coursescanadd(){
    if (coursesData.length  > 0) {
  table = document.getElementById('myTable')
  table.getElementsByTagName('thead')[0].innerHTML = '<tr><th scope="col"> # </th><th scope="col"> المقررات التي يمكن اضافتها حسب الجدول الدراسي</th><th scope="col"> الشعبة</th><th scope="col"> مواعيد المحاضرات</th> <th scope="col">استاذ المادة</th></tr>'


  table = table.getElementsByTagName('tbody')[0]
  table.innerHTML = ""

  rowspannum = 0
  i = 0 
  k = 1
  while (i < coursesData.length ){
    row = table.insertRow(table.rows.length)
   coll0 = row.insertCell()
   coll0.innerHTML = k
   coll1 = row.insertCell()
   coll1.innerHTML = coursesData[i][2]
 
    time = ''
    for( h = 5 ; h <= 9 ; h++){
      if(coursesData[i][h] != '-'){

        time = time + columnsData[h] + ": " + coursesData[i][h] + " "
      }
    }
    row.insertCell().innerHTML = '<div class="form-check"><input onclick = "coursesDatanotValueCH()" class="form-check-input" type="checkbox" value="'+coursesData[i][2]+'" id="'+coursesData[i][3] +'"><label class="form-check-label" for="flexCheckDefault">'+ coursesData[i][3] + '</label></div>'
    row.insertCell().innerHTML = time
    row.insertCell().innerHTML = coursesData[i][4] 
    
    rowspannum = 1
    while (i+1 < coursesData.length && coursesData[i][2] == coursesData[i+1][2]  ){
      row1 = table.insertRow(table.rows.length)

          time = '' 
          for( h = 5 ; h <= 9 ; h++){
      if(coursesData[i+1][h] != '-'){

        time = time  + columnsData[h] + ": " + coursesData[i+1][h] + " "
      }
    }
    
     

      rowspannum++   
       
    row1.insertCell(-1).innerHTML = '<div class="form-check"><input onclick = "coursesDatanotValueCH()" class="form-check-input" type="checkbox" value="'+coursesData[i][2]+'" id="'+coursesData[i+1][3] +'"><label class="form-check-label" for="flexCheckDefault">'+ coursesData[i+1][3] + '</label></div>'
    row1.insertCell(-1).innerHTML = time
    row1.insertCell(-1).innerHTML = coursesData[i+1][4] 
    i++
  }
  
  if (rowspannum > 1){
    
  coll0.rowSpan = rowspannum
  coll1.rowSpan = rowspannum  
  }
 
  coll0.style.cssText = 'vertical-align: middle'
  coll1.style.cssText = 'vertical-align: middle'
    i++
    k++
    
  }
    if (htmlcode != ''){
      document.getElementById('but').innerHTML = htmlcode
}
     document.getElementById('ms1').innerText = ms
        if (!avlAddDreap){

    document.getElementById('add').setAttribute("disabled", "disabled")
}

}
  else{
      htmlcode = document.getElementById('but').innerHTML
        document.getElementById('but').innerHTML = ''
    document.getElementById('re').innerText = mes
    table = document.getElementById('myTable')
    table.getElementsByTagName('thead')[0].innerHTML = ''
    table.getElementsByTagName('tbody')[0].innerHTML = ''


  }
 }
function coursesDatanotValueCH (){
     radich = document.querySelector("input[type='radio'][name='radio-stacked1']:checked").value;
        corsaa = []
     reg1 = reg
          table = document.getElementById('myTable')
          table = table.getElementsByTagName('tbody')[0]
          rows = table.getElementsByTagName('tr')
          
          radios = document.querySelectorAll('input[type=checkbox]')
           
 
          for(i = 0 ; i < radios.length ; i++) {
            if((!radios[i].checked) && (radios[i].hasAttribute('disabled'))){
              radios[i].removeAttribute('disabled')
            }

          }

          cors = []
          sh = []
          for(i = 0 ; i < radios.length ; i++) {

            if(radios[i].checked){
              value = radios[i].getAttribute('value')
              id = radios[i].getAttribute('id')

              index = -1
              for(j = 0 ; j < coursesDataTable.length ; j++){
                    if (coursesDataTable[j][2] == value && coursesDataTable[j][3] == id ){
                      cors.push(coursesDataTable[j][2])
                      sh.push(coursesDataTable[j][3])
                        if (radich == 'الشعب المتعارضة'){
                        corsaa.push(coursesDatanot[j][0][2])
                        }
                     // corsechace.push(coursesData[j])
                     reg1 += coursesDataTable[j][coursesDataTable[j].length-1]
                     index = j
                      break
                    }
              }
              for(j = 0 ; j < coursesDataTable.length ; j++){
                if (coursesDataTable[j][2] != value){


              for( h = 5 ; h <= 9 ; h++){

                
               if(coursesDataTable[j][h] != '-' && coursesDataTable[index][h] != '-'){
                
                a = coursesDataTable[j][h].split('-')
                a2 = coursesDataTable[index][h].split('-')

                
               // if((a[0] <= a2[0] <= a[1]) || (a[0] <= a2[1] <= a[1]) || (a2[0] <= a[0] <= a2[1]) || (a2[0] <= a[1] <= a2[1])){
                  if((a[0] >= a2[0] && a[0] <= a2[0])|| (a2[0] >= a[0] && a2[0] <= a[0])){
                    for(k = 0 ; k < radios.length ; k++) {
                    value = radios[k].getAttribute('value')
                      id = radios[k].getAttribute('id')
                    if (coursesDataTable[j][2] == value && coursesDataTable[j][3] == id ){
                      
                      radios[k].setAttribute('disabled','disabled')
                    }
                  }
                      // **************
                    }
                  }
                  

                }


        
                
            }
                    }
              }
            }    
            
      
  for(i = 0 ; i < radios.length ; i++) {

if(!radios[i].checked){
  value = radios[i].getAttribute('value')
  for(j = 0 ; j < coursesDataTable.length ; j++){
                if (coursesDataTable[j][2] == value){

                  if(coursesDataTable[j][coursesDataTable[j].length-1]+reg1 > max){
                    radios[i].setAttribute('disabled','disabled')
                    
                  }

}}
}

            }
          
        
          for(j = 0 ; j < rows.length ; j++ ){
           if(cors.includes(rows[j].getElementsByTagName('td')[1].innerText)){
            index = cors.indexOf(rows[j].getElementsByTagName('td')[1].innerText)
            for(k = 0 ; k < radios.length ; k ++){
                  if(radios[k].getAttribute('id') != sh[index] && radios[k].getAttribute('value') == cors[index]  ){
                    
                    radios[k].setAttribute('disabled','disabled')
                  }
                }
           }
          }    


           cru = ''
      che = ''
      crudelet = ''
          for(i = 0 ; i < cors.length ; i++){
              cru += cors[i]+','
              che += sh[i]+','
          }
           for(i = 0 ; i < corsaa.length ; i++){
             crudelet += corsaa[i]+','
           }
          document.getElementById('cr').value = cru
          document.getElementById('sh').value = che
          document.getElementById('crd').value = crudelet
       }
       function disabledButton() {

    OKButton = document.getElementById('ok')

    if (OKButton.hasAttribute('disabled')) {
      OKButton.removeAttribute('disabled')
    }

    else {
      OKButton.setAttribute("disabled", "disabled")

    }


  }

