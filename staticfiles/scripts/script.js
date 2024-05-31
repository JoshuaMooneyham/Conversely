let msgForm = document.getElementById('send-message');
let textBox = msgForm.querySelector('textarea');
let updateMsgForm = document.getElementById('update-message');
let updateTextBox = updateMsgForm.querySelector('textarea');
let message;

// function scrollToBottom() {
//     window.scrollBy({
//         "top": 99999999,
//         "left": 0,
//         "behavior": "smooth"
//     })
// }

// function scrollToBottom2() {
//     const body = document.querySelector('body');
//     body.scrollTop = body.scrollHeight;
// }

function swapBars() {
    msgForm.classList.toggle('hidden');
    updateMsgForm.classList.toggle('hidden');
}

textBox.onkeydown = (e) => {
    if (e.keyCode == 13 && !e.shiftKey) {
        e.preventDefault();
    }
}

updateTextBox.onkeydown = (e) => {
    if (e.keyCode == 13 && !e.shiftKey) {
        e.preventDefault();
    }
}

addEventListener("htmx:wsAfterSend", () => {
    textBox.value = '';
    // scrollToBottom()
    console.log('send')
})

addEventListener("click", (e) => {
    if (e.target.classList.contains('edit_message')) {
        message = e.target.closest('div');
        if (updateMsgForm.classList.contains('hidden')) {
            swapBars()
        }
        updateTextBox.innerText = message.querySelector('p').innerText;
        updateTextBox.setSelectionRange(message.querySelector('p').innerText.length, message.querySelector('p').innerText.length)
        updateTextBox.focus()
        document.getElementById('update_message_id').value = message.id.replace('message_', '');
        updateMsgForm.setAttribute('hx-target', `#${message.id}`);
        htmx.process(updateMsgForm);
    }
})