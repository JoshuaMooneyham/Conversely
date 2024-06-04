let msgForm = document.getElementById('send-message');
let textBox = msgForm.querySelector('textarea');
let updateMsgForm = document.getElementById('update-message');
let updateTextBox = updateMsgForm.querySelector('textarea');
let TBB = document.getElementById('to-bottom-btn');
let file_upload_form = document.getElementById('file_input_form');
let message;
let scrollLock;
let messageContainer = document.getElementById('messages_container');
let closeBtn = document.getElementById('close_message_edit');
closeBtn.onclick = function () {
    swapBars()
}

document.addEventListener('DOMContentLoaded', () => {
    textBox.focus()
})


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

TBB.onclick = () => {scrollToBottom('smooth')};

function handleHover() {
    buttons.style.display = 'flex';
}

function handleUnhover() {
    buttons.style.display = 'none';

}


let messageObserver = new MutationObserver((e) => {
    // console.log(e);
    if (!scrollLock) {
        scrollToBottom()
    }

// DELETE
    let messages = [...document.getElementsByClassName('message_wrapper')];
    messages.forEach((msg) => {
        let buttons = msg.querySelector('.message_buttons');
        msg.removeEventListener('mouseover', handleHover)
        msg.removeEventListener('mouseleave', handleUnhover)
        msg.addEventListener('mouseover', (e) => {
            buttons.style.display = 'flex';
        })
        msg.addEventListener('mouseleave', (e) => {
            buttons.style.display = 'none';
        })
    })
})

// DELETE
let messages = [...document.getElementsByClassName('message_wrapper')];
messages.forEach((msg) => {
    let buttons = msg.querySelector('.message_buttons');
    msg.addEventListener('mouseover', (e) => {
        buttons.style.display = 'flex';
    })
    msg.addEventListener('mouseleave', (e) => {
        buttons.style.display = 'none';
    })
})

messageObserver.observe(messageContainer, {childList: true})

function scrollToBottom(behavior) {
    messageContainer.scrollBy({'top': messageContainer.scrollHeight, "left": 0, "behavior": behavior})
}

scrollToBottom();

messageContainer.onchange = (e) => {
    console.log(e)
}

function swapBars() {
    msgForm.classList.toggle('hidden');
    updateMsgForm.classList.toggle('hidden');
    if (!msgForm.classList.contains('hidden')) {
        textBox.focus();
    }
    file_upload_form.classList.toggle('hidden');
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
    if (e.target.classList.contains('edit_message') || e.target.classList.contains('fa-pencil')) {
        console.log(e.target)
        message = e.target.classList.contains('edit_message') ? e.target.parentElement.parentElement : e.target.parentElement.parentElement.parentElement;
        console.log(message)
        if (updateMsgForm.classList.contains('hidden')) {
            swapBars()
        }
        updateTextBox.value = '';
        updateTextBox.value = message.querySelector('p').innerText;
        updateTextBox.setSelectionRange(message.querySelector('p').innerText.length, message.querySelector('p').innerText.length)
        updateTextBox.focus()
        document.getElementById('update_message_id').value = message.id.replace('message_', '');
        updateMsgForm.setAttribute('hx-target', `#${message.id}`);
        htmx.process(updateMsgForm);
    } else {
        let account = document.getElementById('account');
        if (!e.target === account || ![...account.childNodes, account, account.querySelector('#ban_user_btn'), account.querySelector('#unban_btn')].includes(e.target)) {
            console.log('hiding', account.childNodes)
            account.classList.add('hidden');
        }
    }
})

function closePopup() {
    document.getElementById('account').classList.add('hidden');
}

let file_upload = document.getElementById('file_input');
let file_btn = document.getElementById('file_upload_btn');
let submit_file_btn = document.getElementById('submit_file_btn');
file_btn.onclick = function () {
    file_upload.click()
}

file_upload.onchange = () => {
    console.log(file_upload)
    if (file_upload.value !== '') {
        submit_file_btn.classList.remove('hidden');
    } else {
        submit_file_btn.classList.add('hidden');
    }
}