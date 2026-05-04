// Switching tabs
const tabs = document.querySelectorAll(".tab");
const contents = document.querySelectorAll(".tab-content");
const themeToggler = document.querySelector(".theme-toggler")
tabs.forEach(tab => {
    tab.addEventListener("click", () => {

        // Remove ctive from all tabs
        tabs.forEach(t => t.classList.remove("active"));

        // Hide all content
        contents.forEach(c => c.classList.remove("active"));

        // Activate clicked tab
        tab.classList.add("active");

        // Show matching content
        const target = document.getElementById(tab.dataset.tab);
        if (target) {
            target.classList.add("active");
        }
    })
})

//  Change themes
themeToggler.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme-variables");

    themeToggler.querySelector("span:nth-child(1)").classList.toggle("active");
    themeToggler.querySelector("span:nth-child(2)").classList.toggle("active");
})
