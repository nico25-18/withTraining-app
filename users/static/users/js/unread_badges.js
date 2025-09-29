function updateUnreadBadges() {
  fetch('/chatrooms/unread_counts/')
    .then(response => response.json())
    .then(data => {
      const chatrooms = data.chatrooms;

      for (const item of chatrooms) {
        const latestMsg = document.getElementById(`latest-msg-${item.room_id}`);
        if (!latestMsg) continue;

        latestMsg.textContent = item.latest_message;

        const badge = document.getElementById(`unread-badge-${item.room_id}`);
        if (!badge) continue;

        if (item.unread_count > 0) {
          badge.textContent = item.unread_count;
          badge.style.display = 'inline-block';
        } else {
          badge.style.display = 'none';
        }
      }
    });
}

// 起動時と定期実行（5秒ごと）
document.addEventListener('DOMContentLoaded', () => {
  updateUnreadBadges();
  setInterval(updateUnreadBadges, 5000);
});