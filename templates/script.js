let xhr = new XMLHttpRequest();
xhr.open("POST", "https://reqbin.com/echo/post/json");
xhr.setRequestHeader("Accept", "application/json");
xhr.setRequestHeader("Content-Type", "application/json");
var messages = document.getElementById("messages");
var textbox = document.getElementById("textbox");
var button = document.getElementById("button");
xhr.onreadystatechange = function () {
     if (xhr.readyState === 4) {
       console.log(xhr.status);
       console.log(xhr.responseText);
     }};

button.addEventListener("click", function(){
     var newMessage = document.createElement("li");
     newMessage.innerHTML = textbox.value;
     messages.appendChild(newMessage);
     textbox.value = "";
     xhr.send(newMessage)

});