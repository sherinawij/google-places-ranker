const sortOption = document.getElementById("sort-option")
const placesId = document.getElementById("places-id")
if (sortOption) {
    sortOption.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-sort]");
        if(!button){
            return;
        }
        for(const other of sortOption.querySelectorAll("button")){
            other.classList.toggle("active", other === button);
        }
        const sortValue = button.dataset.sort;
        if(sortValue == "weighted"){
            results.sort((a,b) =>{
                if(a.score == null){
                    return 1;
                }
                if(b.score == null){
                    return -1;
                }
                return b.score - a.score;
            });
        }
        if(sortValue == "rating"){
            results.sort((a,b) =>{
                if(a.rating == null){
                    return 1;
                }
                if(b.rating == null){
                    return -1;
                }
                return b.rating - a.rating;
            });
        }
        if(sortValue == "review"){
            results.sort((a,b) =>{
                if(a.review_count == null){
                    return 1;
                }
                if(b.review_count == null){
                    return -1;
                }
                return b.review_count - a.review_count;
            });
        } 
        loadMissingSummaries(results.slice(0, 5));
    });
}
function loadMissingSummaries(places){
    for(const place of places){
        if(place.summary){
            continue;
        }
        place.summary = "Loading summary...";
        fetch(`/summary?query=${encodeURIComponent(query)}&id=${encodeURIComponent(place.id)}`)
            .then(response => response.ok ? response.json() : Promise.reject())
            .then(data => { place.summary = data.summary; })
            .catch(() => { place.summary = "Summary temporarily unavailable."; })
            .finally(() => renderResults(results));
    }
    renderResults(results);
}
function renderResults(places){
    placesId.innerHTML = "";
    for(const place of places){
        const div = document.createElement("div");
        const name = document.createElement("p");
        name.textContent = place.name;
        const address = document.createElement("p");
        address.textContent = place.address;
        const rating = document.createElement("p");
        rating.textContent = `Rating: ${place.rating}`
        const review_count = document.createElement("p");
        review_count.textContent = `Review Count: ${place.review_count}`
        const score = document.createElement("p");
        score.textContent = `Score: ${place.score}`
        const openNow = document.createElement("p");
        if(place.open_now == null){
            openNow.textContent = "Hours unavailable";
        } else {
            openNow.textContent = place.open_now ? "Open Now" : "Closed";
        }
        const hours = document.createElement("ul");
        for(const day of place.opening_hours || []){
            const li = document.createElement("li");
            li.textContent = day;
            hours.appendChild(li);
        }
        div.appendChild(name);
        div.appendChild(address);
        div.appendChild(rating);
        div.appendChild(review_count);
        div.appendChild(score);
        if(place.summary){
            const summary = document.createElement("p");
            summary.textContent = `Review: ${place.summary}`
            div.appendChild(summary);
        }
        div.appendChild(openNow);
        div.appendChild(hours);
        placesId.appendChild(div);
    }   
}