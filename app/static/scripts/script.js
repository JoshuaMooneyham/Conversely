let msgForm = document.getElementById('send-message');
let textBox = msgForm.querySelector('textarea');
let updateMsgForm = document.getElementById('update-message');
let updateTextBox = updateMsgForm.querySelector('textarea');
let message;
let scrollLock;

let messageContainer = document.getElementById('messages_container');

messageContainer.onscroll = (e) => {
    // console.log(e.target.scrollTop + e.target.clientHeight, e.target.scrollHeight)
    currentHeight = e.target.scrollTop + e.target.clientHeight;
    maxHeight = e.target.scrollHeight;
    scrollLock = maxHeight - currentHeight > 3;
}

let messageObserver = new MutationObserver((e) => {
    // console.log(e);
    if (!scrollLock) {
        scrollToBottom()
    }
})

messageObserver.observe(messageContainer, {childList: true})

function scrollToBottom(behavior) {
    messageContainer.scrollBy({'top': messageContainer.scrollHeight, "left": 0, "behavior": behavior})
}

scrollToBottom();
// document.addEventListener('DOMContentLoaded', () => {
// })

messageContainer.onchange = (e) => {
    console.log(e)
}

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