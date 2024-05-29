let msgForm = document.getElementById('send-message');
let textBox = msgForm.querySelector('textarea');

textBox.onkeydown = (e) => {
    if (e.keyCode == 13 && !e.shiftKey) {
        e.preventDefault();
    }
}

addEventListener("htmx:wsAfterSend", () => {
    textBox.value = '';
})