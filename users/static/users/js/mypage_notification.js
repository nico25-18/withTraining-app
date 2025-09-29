function updateNotificationBadges() {
  fetch('/mypage/unread_counts/')
    .then(response => response.json())
    .then(data => {
      const notifications = data.unread_notification_count;

      const badge = document.getElementById('unread-badge');
      if (!badge) return;
      
      if (notifications > 0){
        badge.textContent = notifications;
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }
    });
}

// 起動時と定期実行（5秒ごと）
document.addEventListener('DOMContentLoaded', () => {
  updateNotificationBadges();
  setInterval(updateNotificationBadges, 5000);
});