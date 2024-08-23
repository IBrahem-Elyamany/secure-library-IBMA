function myMenuFunction() {
  var i = document.getElementById("navMenu");

  if (i.className === "nav-menu") {
    i.className += " responsive";
  } else {
    i.className = "nav-menu";
  }
}

function signin() {
  window.location.href = "signin";
}
function signup() {
  window.location.href = "signup";
}
