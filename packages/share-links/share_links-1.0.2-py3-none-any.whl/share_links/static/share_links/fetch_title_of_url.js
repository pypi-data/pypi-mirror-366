window.addEventListener("load", function () {
    // add autofetch title button
    let title_row = document.getElementsByClassName("fieldBox field-title")[0]
    let fakeBtn = document.createElement("div")
    fakeBtn.classList = "button-add-title"
    fakeBtn.innerHTML = "↺"
    fakeBtn.title = "Auto fill title field from url"
    title_row.appendChild(fakeBtn)

    fakeBtn.addEventListener("click", function () {
        getTitle()
    })

    // add autofetch language button
    let lang_row = document.getElementsByClassName("fieldBox field-language")[0]
    let anotherFakeBtn = document.createElement("div")
    anotherFakeBtn.classList = "button-add-lang"
    anotherFakeBtn.innerHTML = "↺"
    anotherFakeBtn.title = "Auto fill lang field from url"
    lang_row.appendChild(anotherFakeBtn)

    anotherFakeBtn.addEventListener("click", function () {
        getLang()
    })

    // add button to autofetch all data if possible
    let all_row = document.getElementsByClassName("form-row field-link")[0]
    let aThirdFakeBtn = document.createElement("div")
    aThirdFakeBtn.classList = "button-add-all"
    aThirdFakeBtn.innerHTML = "Fetch all"
    aThirdFakeBtn.title = "Auto fill title & lang fields from url"
    all_row.firstElementChild.appendChild(aThirdFakeBtn)

    aThirdFakeBtn.addEventListener("click", function () {
        getLang()
        getTitle()
    })

    urlAutofill = new URLSearchParams(window.location.search)
    if (urlAutofill.get("autofill") !== null) {
        getLang()
        getTitle()
    }

})

function createInformationalElement(element, text, id, status) {
    let p = document.getElementById(id)
    if (p === null) {
        p = document.createElement("p")
        p.id = id
        element.parentElement.parentElement.after(p)
    }
    p.style.fontStyle = "italic"
    p.style.fontSize = "0.8em"
    if (status === false) {
        p.style.color = "#faa"
    }
    else if (status === true) {
        p.style.color = "#afa"
    }
    else {
        p.style.color = "#fff"
    }
    p.innerHTML = text
}

const getTitle = () => {
    let link_input = document.getElementById("id_link")
    let title_input = document.getElementById("id_title")
    createInformationalElement(title_input, "Getting title...", "title-info", null)
    if (link_input.value !== "") {
        // TODO: get urls of the api request instead of hardcoding it
        return fetch(`/en/get-title/?url=${link_input.value}`)
            .then((response) => response.json())
            .then((answer) => {
                if (answer.status === "ok") {
                    if (answer.title.length < 2000) {
                        title_input.value = answer.title
                        createInformationalElement(title_input, "Success!", "title-info", true)
                    }
                    else {
                        createInformationalElement(title_input, "Error: title is too long (> 2000 chars).", "title-info", false)
                    }
                }
                else {
                    createInformationalElement(title_input, "Error: " + answer.status, "title-info", false)
                }
            }
            )
    }
}

const getLang = () => {
    let link_input = document.getElementById("id_link")
    let lang_input = document.getElementById("id_language")
    createInformationalElement(lang_input, "Searching for lang...", "lang-info", null)
    if (link_input.value !== "") {
        // TODO: get urls of the api request instead of hardcoding it
        return fetch(`/en/get-lang/?url=${link_input.value}`)
            .then((response) => response.json())
            .then((answer) => {
                if (answer.status === "ok") {
                    if (answer.lang.length < 5) {
                        lang_input.value = answer.lang
                        createInformationalElement(lang_input, "Success!", "lang-info", true)
                    }
                    else {
                        createInformationalElement(lang_input, "Error: lang is too long (> 5 chars).", "lang-info", false)
                    }
                }
                else {
                    createInformationalElement(lang_input, "Error: " + answer.status, "lang-info", false)
                }
            }
            )
    }
}
