let msgForm = document.getElementById('send-message');
let textBox = msgForm.querySelector('textarea');
let updateMsgForm = document.getElementById('update-message');
let updateTextBox = updateMsgForm.querySelector('textarea');
let TBB = document.getElementById('to-bottom-btn');
let message;
let scrollLock;
let messageContainer = document.getElementById('messages_container');

messageContainer.onscroll = (e) => {
    // console.log(e.target.scrollTop + e.target.clientHeight, e.target.scrollHeight)
    currentHeight = e.target.scrollTop + e.target.clientHeight;
    maxHeight = e.target.scrollHeight;
    scrollLock = maxHeight - currentHeight > 3;
    if (!scrollLock) {
        TBB.classList.add('hidden');
    } else {
        TBB.classList.remove('hidden');
    }
}

// let showBlockedMsg = [...document.getElementsByClassName('block-i')];
        
// showBlockedMsg.forEach((iTag) => {
//     iTag.onclick = (e) => {
//         let content = e.target.closest('div').querySelector('.blocked-content');
//         content.classList.toggle('hidden');
//         e.target.innerText = e.target.innerText === 'Hide' ? 'Show' : 'Hide' ;
//         }
//     }
// )

TBB.onclick = () => {scrollToBottom('smooth')};

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
    scrollToBottom()
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
    } else {
        let account = document.getElementById('account');
        if (!e.target === account || ![...account.childNodes].includes(e.target)) {
            account.classList.add('hidden');
        }
    }
})

function closePopup() {
    document.getElementById('account').classList.add('hidden');
}