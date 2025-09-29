document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('chat-form');
  const textArea = document.getElementById('chat-text');
  const container = document.querySelector('.chat-messages');
  const roomId = form.dataset.roomId;
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  container.scrollTop = container.scrollHeight;
  
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const text = textArea.value.trim();
    if (!text) return;

    const url = `/chatrooms/${roomId}/send/`;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ 'text': text })
    })
    .then(res => res.json())
    .then(data => {
      if (data) {
        appendMessage(data, true);
        textArea.value = '';
      }
    })
    .catch(error => {
      alert("送信に失敗しました");
      console.error(error);
    });
  });

  let lastTimestamp = new Date().toISOString(); // 初期時刻：ページ表示時

  function fetchNewMessages() {
    fetch(`/chatrooms/${roomId}/messages/?since=${encodeURIComponent(lastTimestamp)}`)
      .then(res => res.json())
      .then(data => {
        if (data.messages && data.messages.length > 0) {
          data.messages.forEach(msg => {
            appendMessage(msg, false);
            lastTimestamp = new Date().toISOString(); // 直近時刻を更新
          });
        }
        if (data.read_ids && data.read_ids.length > 0) {
            data.read_ids.forEach(id => {
                const msgElem = document.querySelector(`#msg-${id}`);
                if (msgElem) {
                    const smallTag = msgElem.querySelector('small');
                    if (smallTag && !smallTag.textContent.includes('✔️')) {
                        smallTag.textContent += '✔️ 既読';  // 既読マーク追加
                    }
                }
            });
        }
      })
      .catch(err => console.error('新着取得エラー:', err));
  }

  // 5秒ごとに新着取得
  setInterval(fetchNewMessages, 5000);

  function appendMessage(msg, is_right) {
    const msgDiv = document.createElement('div');
    
    msgDiv.id = `msg-${msg.id}`;
    msgDiv.classList.add('message-container');
    if (is_right){
        msgDiv.classList.add('message-right');

        if (msg.is_read){
            msgDiv.innerHTML = `
            <small style="margin-top: auto; margin-right: 5px;">✔️ 既読</small>
            <div class="message-bubble">
                ${msg.message}
            </div>
            `;
        }
        else {
            msgDiv.innerHTML = `
            <small style="margin-top: auto; margin-right: 5px;"> </small>
            <div class="message-bubble">
                ${msg.message}
            </div>
            `;
        }
    } else {
        msgDiv.classList.add('message-left');
        msgDiv.innerHTML = `
        <div class="message-bubble">
            ${msg.message}
        </div>
        `;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
  }
});