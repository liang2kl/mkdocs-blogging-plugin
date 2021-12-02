var currentPage = 0
const lastComponent = window.location.href.split("/").slice(-1).pop()

if (lastComponent && lastComponent.slice(0, 7) == "#blog-p") {
  const page = parseInt(lastComponent.slice(7))
  if (page) {
    currentPage = page - 1
  }
}

function scrollToTop() {
  setTimeout(function () {
    window.scrollTo(0, 0);
  }, 100);
}

var pagination = document.getElementById("blog-pagination");
if (pagination) {
  var links = pagination.getElementsByClassName("page-number");
  if (links.length) {
    for (var i = 0; i < links.length; i++) {
      // Toggle pagination highlight
      links[i].addEventListener("click", function () {
        var current = pagination.getElementsByClassName("active");
        if (current.length) {
          current[0].className = current[0].className.replace(
            " active", ""
          );
        }
        this.className += " active";

        // Togglg visibility of pages
        const destPage = parseInt(this.textContent)
        var pages = document.getElementsByClassName("page")
        if (destPage && pages.length) {
          for (var j = 0; j < pages.length; j++) {
            const pageId = parseInt(pages[j].id.replace("page", ""))
            if (pageId != destPage) {
              // This is not the destination page
              if (!pages[j].className.includes("blog-hidden")) {
                pages[j].className += " blog-hidden"
              }
            } else {
              // This is the destination page
              pages[j].className = pages[j].className.replace(" blog-hidden", "")
            }
            scrollToTop();
          }
        }
      });
    }
    links[currentPage].className += " active"
    links[currentPage].click();
  }
}
