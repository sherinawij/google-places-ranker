const sortOption = document.getElementById("sort-option")
const placesId = document.getElementById("places-id")
if (sortOption) {
    sortOption.addEventListener("change", () => {
        if(sortOption.value == "weighted"){
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
        if(sortOption.value == "rating"){
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
        if(sortOption.value == "review"){
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
        renderResults(results);
    });
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
        div.appendChild(name);
        div.appendChild(address);
        div.appendChild(rating);
        div.appendChild(review_count);
        div.appendChild(score);
        placesId.appendChild(div);
    }   
}