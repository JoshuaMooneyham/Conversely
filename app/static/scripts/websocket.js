const group_name = JSON.parse(document.getElementById('group_name').textContent);
const webSocket = new WebSocket(
    `ws://${window.location.host}/ws/group/${group_name}/`
);

webSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(e.data)
    // document.querySelector('#messages_container').innerHTML += (data.)
}