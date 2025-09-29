document.addEventListener('DOMContentLoaded', function () {
  // CSRFトークン取得用（Django標準）
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  document.querySelectorAll('.btn-like').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();

      const targetUserId = this.dataset.userId;
      const btnElement = this;

      fetch("/ajax/toggle_like/", {
        method: "POST",
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken
        },
        body: `to_user_id=${targetUserId}`
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          if (data.liked) {
            btnElement.textContent = '💔 いいねを取り消す';
            btnElement.title = 'いいねを取り消す';
          } else {
            btnElement.textContent = '❤️ いいねする';
            btnElement.title = 'いいねする';
          }
        } else {
          alert("操作に失敗しました：" + data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert("通信エラーが発生しました。");
      });
    });
  });
});