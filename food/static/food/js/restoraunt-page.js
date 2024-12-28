function selectFoodCategory(element){
    element.classList.toggle("selected")

    const pathList = window.location.pathname.split("/");
    const citySlug = pathList[1];
    const restorauntSlug = pathList[3]

    let categories = '';

    document.querySelectorAll(".nav-pills li.selected").forEach(
        a => {
            categories += $(a).attr("data-id") + ","
        }
    )

    if (categories[categories.length - 1] == ","){
        console.log(categories)
        categories = categories.slice(0, categories.length - 1)
        console.log(categories)
    }
    fetch(`/api/dishes?restoraunt=${restorauntSlug}&city=${citySlug}&categories=${categories}`).then(
        response => response.json()
    ).then(
        response => {
            document.querySelector(".product-details-box-list").innerHTML = response.content
        }
    )
}
