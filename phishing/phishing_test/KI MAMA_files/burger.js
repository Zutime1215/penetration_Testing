const hamburger_icon = document.querySelector('#nav-bar .nav-bar .nav-list .hamburger');
const nav_list = document.querySelector('#nav-bar .nav-bar .nav-list');

hamburger_icon.addEventListener('click', () => {
	nav_list.classList.toggle('open');
	hamburger_icon.classList.toggle('active');
});




// slider
// sliders
// slider  ///////////////////////////////////////////////////////////
// slider ////////////////////////////////////////////////////////////
var counter = 1;
setInterval(function(){
  document.getElementById('radio' + counter).checked = true;
  counter++;
  if(counter > 4){
	counter = 1;
  }
}, 4200);



// back page function////////////////
function goBack() {
  window.history.back();
}



