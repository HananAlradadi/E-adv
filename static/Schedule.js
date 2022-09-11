
if (!avlAddDreap){

    document.getElementById('add').setAttribute("disabled", "disabled")
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
  document.getElementsByTagName('select')[0].addEventListener('change', function (evant) {
    var fTable = evant.target.value
    if (fTable == 'الجدوال بالشعب المتاحة' && avlAddDreap) {

      document.getElementById('add').removeAttribute('disabled')

    }
    else if (fTable == 'الجدوال مع طلب توسعه') {
      document.getElementById('add').setAttribute("disabled", "disabled")

    }
    else if (fTable == 'الجدوال بالشعب المتاحة بايام اوف' && avlAddDreap) {

      document.getElementById('add').removeAttribute('disabled')

    }
    else {

      document.getElementById('add').setAttribute("disabled", "disabled")

    }

  })


