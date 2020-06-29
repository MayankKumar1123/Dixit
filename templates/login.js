
// Sign In Page Elements
////////////////////////////////////////////////////////////////////////////
// Divs
let joinDiv = document.getElementById('join-game')
let joinErrorMessage = document.getElementById('error-message')
// Input Fields
let joinNickname = document.getElementById('join-nickname')
let joinRoom = document.getElementById('join-room')
let joinPassword = document.getElementById('join-password')
// Buttons
let joinEnter = document.getElementById('join-enter')
let joinCreate = document.getElementById('join-create')




// User Creates Room
joinCreate.onclick = function(){    
  var payload = {
        'type': {{messageTypes.createRoom}} ,
        'nickname':joinNickname.value,
        'room':joinRoom.value,
        'password':joinPassword.value
    } 
    // Make the request to the WebSocket.
    //ws.send(JSON.stringify(payload));
    
    $.post('/getGame',payload ,function(data){
        console.log(data)
        var obj = JSON.parse(data)
        if (obj.game == 'exists'){
            window.alert("Game Already Exists")
        }else{
            //reload to next page
            window.location.href = "/gameBoard";
        }
    });
}
// User Joins Room
joinEnter.onclick = function(){    
  var payload = {
        'type': {{messageTypes.enterRoom}} ,
        'nickname':joinNickname.value,
        'room':joinRoom.value,
        'password':joinPassword.value
    } 
    $.post('/getGame',payload ,function(data){
        console.log(data)
        var obj = JSON.parse(data)
        if (obj.game == 'na'){
            window.alert("Game doesn't exist")
        }else{
            //reload to next page
            window.location.href = "/gameBoard";
        }        
    });
}





