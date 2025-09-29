document.addEventListener('DOMContentLoaded', function () {
    const checkAll = document.getElementById('check-all');
    const targetRead = document.getElementById('mark_read');
    const targetDelete = document.getElementById('delete');
    const checkboxes = document.querySelectorAll('.check-notification');
    const notificationItems = document.querySelectorAll('.notification-item');

    notificationItems.forEach(item => {
        item.addEventListener('click', function (e) {
            // チェックボックスにチェック
            const checkbox = this.querySelector('.check-notification');
            if (checkbox) {
                if (
                    !(e.target.tagName === 'INPUT' && e.target.type === 'checkbox')
                    && e.target.tagName !== 'LABEL'
                    && e.target.tagName !== 'STRONG'
                    && e.target.tagName !== 'SMALL')
                {
                    checkbox.checked = !checkbox.checked;
                }

                if (checkbox.checked) {
                    // 未読→既読にした場合、既読にする
                    if (item.classList.contains('unread')) {
                        notificationId = item.dataset.id;
                        fetch(`/notifications/mark_read/${notificationId}/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': '{{ csrf_token }}', // テンプレートからトークンを埋め込む
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({}),
                        })
                            .then(res => {
                                if (res.ok) {
                                    item.classList.remove('unread');
                                    item.classList.add('is_read')
                                }
                            })
                            .catch(err => {
                                console.error('既読処理に失敗:', err);
                            });
                    }

                }
            }
        })
    });

    checkAll.addEventListener('change', function () {
        checkboxes.forEach(cb => cb.checked = checkAll.checked);
    });

    targetRead.addEventListener('click', function () {
        const selectedIds = Array.from(document.querySelectorAll('input[name="selected_notifications"]:checked'))
            .map(cb => cb.value);

        fetch('/notifications/mark_target_read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}', // テンプレートからトークンを埋め込む
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: selectedIds })
        })
            .then(res => {
                if (res.ok) {
                    selectedIds.forEach(id => {
                        const target = document.querySelector(`#notification-${id}`);
                        target.classList.remove('unread');
                        target.classList.add('is_read');
                    });
                }
            })
            .catch(err => {
                console.error('既読処理に失敗:', err);
            });
    });

    targetDelete.addEventListener('click', function () {
        const selectedIds = Array.from(document.querySelectorAll('input[name="selected_notifications"]:checked'))
            .map(cb => cb.value);

        fetch('/notifications/mark_target_delete/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}', // テンプレートからトークンを埋め込む
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: selectedIds })
        })
            .then(res => {
                if (res.ok) {
                    // 成功時に該当アイテムを非表示・スタイル変更など
                    selectedIds.forEach(id => {
                        const target = document.querySelector(`#notification-${id}`);
                        target.remove();
                    });

                    // 通知エリア内に通知があるか
                    const notifications = document.getElementById('notification-area');
                    const ul = notifications.querySelector('ul')
                    if (ul.children.length == 0) {
                        const p = document.createElement('p');
                        p.id = "no-notification"
                        p.textContent = '通知はまだありません。';
                        notifications.appendChild(p);
                    }
                }
            })
            .catch(err => {
                console.error('既読処理に失敗:', err);
            });
    });
});