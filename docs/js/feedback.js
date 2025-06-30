const feedback = document.forms.feedback;
feedback.hidden = false;

feedback.addEventListener("submit", function(ev) {
    ev.preventDefault();
    const commentElement = document.getElementById("feedback");
    commentElement.style.display = "block";
    feedback.firstElementChild.disabled = true;
    const data = ev.submitter.getAttribute("data-md-value");
    const note = feedback.querySelector(".md-feedback__note [data-md-value='" + data + "']");
    if (note) {
        note.hidden = false;
    }
})
