document.getElementById('loginForm')
    .addEventListener('submit', function(event){
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    console.log(username, password)
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/login', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if(response.data.token){
                var cookies = [
                    "token=" + response.data.token + ";",
                    "uid=" + response.data.uid + ";",
                ]
                setCookie(cookies, 7); // 存储 token 到 cookie，有效期为 7 天
                console.log('Token stored in cookie');
                window.location.href = "/";
            }
        }
    };
    var data = JSON.stringify({"username": username, "password": password});
    xhr.send(data);
});

function setCookie(cookies, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "expires=" + date.toUTCString();
    }
    for (var i = 0; i < cookies.length; i++){
        document.cookie = cookies[i]
    }
    document.cookie = expires
}
