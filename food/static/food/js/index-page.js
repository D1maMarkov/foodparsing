const ul = document.querySelector('ul.hints');

function searchRestoraunts(event){
    restoraunt_name = event.target.value;

    if (restoraunt_name.length > 0){
        fetch(`/api/restoraunts?restoraunt_name=${restoraunt_name}`).then(
            response => response.json()
        ).then(
            response => {
                ul.innerHTML = generateResHints(response.restoraunts)

                if (response.restoraunts.length > 0){
                    document.querySelector('input[type=search]').style.borderRadius = "25px 25px 0px 0px"
                }
                else{
                    document.querySelector('input[type=search]').style.borderRadius = "100px"
                }
            }
        )
    }
    else{
        document.querySelector('input[type=search]').style.borderRadius = "100px";
        ul.innerHTML = '';
    }
}


function generateResHints(restoraunts){
    let restorauntsHTML = ``;
    for (let restoraunt of restoraunts){
        restorauntsHTML += `
            <li class="hint"><a href=${restoraunt.ref}>${restoraunt.name} ${restoraunt.address}</a></li>
        `
    }

    return restorauntsHTML
}
