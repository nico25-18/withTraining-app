document.addEventListener("DOMContentLoaded", function () {
  const usernameInput = document.getElementById("id_username");
  const password1Input = document.getElementById("id_password1");
  const password2Input = document.getElementById("id_password2");

  // ユーザー名のリアルタイムチェック
  usernameInput.addEventListener("input", function () {
    const val = this.value;
    const re = /^[ぁ-んァ-ヶa-zA-Z0-9@]{0,50}$/;
    if (!re.test(val)) {
      this.style.borderColor = "red";
    } else {
      this.style.borderColor = "";
    }
  });

  // パスワード一致チェック
  password2Input.addEventListener("input", function () {
    if (password1Input.value !== password2Input.value) {
      this.style.borderColor = "red";
    } else {
      this.style.borderColor = "";
    }
  });
});