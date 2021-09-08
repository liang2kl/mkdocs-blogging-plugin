var currentPage = 0
const lastComponent = window.location.href.split("/").slice(-1).pop()

if (lastComponent && lastComponent.slice(0, 5) == "#page") {
    const page = parseInt(lastComponent.slice(5))
    if (page) {
        currentPage = page - 1
    }
}

var pagination = document.getElementById("pagination");
if (pagination) {
    var links = pagination.getElementsByClassName("page-number");
    if (links.length) {
        for (var i = 0; i < links.length; i++) {
            links[i].addEventListener("click", function () {
                var current = pagination.getElementsByClassName("active");
                if (current.length) {
                    current[0].className = current[0].className.replace(
                        " active", ""
                    );
                }
                this.className += " active";
            });
        }
        links[currentPage].className += " active"
        links[currentPage].click();
    }
}
