// blog/static/blog/js/comments.js
(function () {
  const editButtons = document.getElementsByClassName("btn-edit");
  const commentText = document.getElementById("id_body");
  const commentForm = document.getElementById("commentForm");
  const submitButton = document.getElementById("submitButton");

  if (!commentForm || !commentText || !submitButton) return;

  for (let btn of editButtons) {
    btn.addEventListener("click", (e) => {
      const el = e.currentTarget;
      const commentId = el.dataset.commentId;
      const editUrl = el.dataset.editUrl;
      if (!commentId || !editUrl) return;

      const block = document.getElementById(`comment${commentId}`);
      const existing = block ? block.innerText.trim() : "";

      commentText.value = existing;
      commentForm.setAttribute("action", editUrl);
      commentForm.setAttribute("method", "post");

      submitButton.innerText = "Update";
      submitButton.classList.remove("btn-signup");
      submitButton.classList.add("btn-primary");

      commentForm.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }
})();
