document.addEventListener("DOMContentLoaded", function () {
    let timeout = null;
    const inputField = document.getElementById("id_adres_zoeken");
    const suggestiesContainer = document.getElementById("adres-suggesties");

    inputField.addEventListener("input", function () {
        clearTimeout(timeout);
        const query = inputField.value.trim();

        if (query.length < 3) {
            suggestiesContainer.innerHTML = "";
            return;
        }

        timeout = setTimeout(() => {
            fetch(`/clienten/zoek-adres/?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestiesContainer.innerHTML = "";
                    if (data.results.length > 0) {
                        suggestiesContainer.classList.add("active");
                        data.results.forEach(adres => {
                            const optie = document.createElement("div");
                            optie.classList.add("suggestie");
                            optie.textContent = adres.weergavenaam;

                            optie.addEventListener("click", function () {
                                document.getElementById("id_adres_zoeken").value = adres.weergavenaam;
                                document.getElementById("id_adres_straatnaam").value = adres.straatnaam;
                                document.getElementById("id_adres_huisnummer").value = adres.huisnummer;
                                document.getElementById("id_adres_toevoeging").value = `${ adres.huisletter ?? "" }${adres.huisnummertoevoeging ?? ""}`;
                                document.getElementById("id_adres_postcode").value = `${ adres?.postcode ?? "" }`;
                                document.getElementById("id_adres_plaatsnaam").value = adres.woonplaatsnaam;
                                suggestiesContainer.innerHTML = "";
                                suggestiesContainer.classList.remove("active");

                                // Extra API call for stadsdeel
                                if (adres.nummeraanduiding_id) {
                                    fetch(`/clienten/zoek-stadsdeel/?nummeraanduidingid=${adres.nummeraanduiding_id}`)
                                        .then(response => response.json())
                                        .then(extraData => {
                                            if (extraData.gebiedenStadsdeelNaam) {
                                                document.getElementById("id_adres_stadsdeel").value = extraData.gebiedenStadsdeelNaam;
                                            }
                                        })
                                        .catch(error => console.error("Fout bij ophalen extra gegevens:", error));
                                }

                            });
                            suggestiesContainer.appendChild(optie);
                        });
                    } else {
                        suggestiesContainer.classList.remove("active"); // Hide if no results
                    }
                });
        }, 300);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("id_adres_zoeken");
    const clearBtn = document.getElementById("clear-search");
    const suggestiesContainer = document.getElementById("adres-suggesties")

    clearBtn.addEventListener("click", function () {
        inputField.value = "";
        suggestiesContainer.classList.remove("active");
        inputField.focus();
        clearBtn.style.display = "none"; // Hide button after clearing
    });

    inputField.addEventListener("input", function () {
        clearBtn.style.display = inputField.value ? "block" : "none";
    });
});