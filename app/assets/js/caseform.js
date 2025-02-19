function setPartnerFieldsVisible(isVisible){
    var elems = document.getElementsByClassName('partner_form_elem');
    var disp = isVisible?"block":"none";
    for(var e in elems){
        if(elems[e].parentNode){
            elems[e].parentNode.setAttribute("style", "display:"+disp);
        }
    }
}
function updateCaseForm(elem){
    setPartnerFieldsVisible(elem.value == 1);
}


window.onload = function() {
    var partnerCheck = document.getElementById('id_partner_check');
    partnerCheck.addEventListener("change", function () {
        updateCaseForm(this);
    });
    setPartnerFieldsVisible(partnerCheck.value == 1);
}
