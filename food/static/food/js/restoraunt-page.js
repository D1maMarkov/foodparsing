function selectFoodCategory(element){
    document.querySelectorAll(".nav-pills li").forEach(
        li => {
            li.classList.remove("selected")
        }
    )

    element.classList.add("selected")

    const pathList = window.location.pathname.split("/");

    let categoryName = '';

    document.querySelectorAll(".nav-pills li.selected a").forEach(
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
