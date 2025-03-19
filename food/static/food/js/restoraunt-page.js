function selectFoodCategory(element){
    document.querySelectorAll(".nav-pills li").forEach(
        li => {
            li.classList.remove("selected")
        }
    )

    element.classList.add("selected")

    const pathList = window.location.pathname.split("/");

    let categoryName = '';

    document.querySelectorAll(".nav-pills li.selected h2").forEach(
        a => {
            categoryName = a.innerHTML;
        }
    )

    document.querySelectorAll(".product-details-box-title").forEach(
        category => {
            if (category.innerHTML.includes(categoryName)){
                category.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    )
}


document.querySelectorAll(".button-container").forEach(button => {
    // Сохраняем изначальное вертикальное положение кнопки
    const rect = button.getBoundingClientRect();
    var originalTop3 = rect.top; // Позиция кнопки относительно начала страницы

    window.addEventListener('scroll', function() {
    var stickyClass3 = 'sticky';
    if (window.pageYOffset > originalTop3) {
        button.classList.add(stickyClass3);
    } else {
        button.classList.remove(stickyClass3);
    }
    });
})