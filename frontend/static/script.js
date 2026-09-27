const sortOption = document.getElementById("sort-option")
const placesId = document.getElementById("places-id")
const podium = document.getElementById("podium")
const howBtn = document.getElementById("how-btn")
const howPanel = document.getElementById("how-panel")
if (howBtn) {
    howBtn.addEventListener("click", () => {
        howPanel.hidden = !howPanel.hidden;
        howBtn.setAttribute("aria-expanded", String(!howPanel.hidden));
        howBtn.classList.toggle("active", !howPanel.hidden);
    });
}
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
        for(const place of results){
            place.rowSummaryOpen = false;
        }
        loadMissingSummaries(results.slice(0, 3));
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
function el(tag, className, text){
    const node = document.createElement(tag);
    if(className){
        node.className = className;
    }
    if(text != null){
        node.textContent = text;
    }
    return node;
}

function todayHours(place) {
    const hours = place.opening_hours;
    if (!hours){
        return null;
    }
    const day = new Date().getDay();
    let index;
    if(day == 0){
        index = 6;
    }
    else{
        index = day-1;
    }
    const line = hours[index];
    if (!line){
        return null;
    }
    return line.split(": ")[1];
}

function statusTag(place) {
    if (place.open_now == null) {
        return el("span", "tag", "HOURS UNKNOWN");
    }
    if (place.open_now) {
        return el("span", "tag green", "OPEN NOW");
    }
    return el("span", "tag red", "CLOSED");
}

function summaryText(place, className) {
    let classes = className;
    if (place.summary == "Loading summary...") {
        classes = className + " loading";
    }
    return el("p", classes, place.summary);
}

function renderRow(place, rank){
    const row = el("div", "row box");
    row.appendChild(el("div", "row-rank", rank));

    const info = el("div", "row-info");
    info.appendChild(el("h2", "row-name", place.name));
    info.appendChild(el("p", "row-address", place.address));
    if(place.rowSummaryOpen && place.summary){
        info.appendChild(summaryText(place, "row-summary"));
    } else {
        const summarize = el("button", "summarize-btn", "📋 SUMMARIZE");
        summarize.type = "button";
        summarize.addEventListener("click", () => {
            place.rowSummaryOpen = true;
            loadMissingSummaries([place]);
        });
        info.appendChild(summarize);
    }
    const hours = todayHours(place);
    if(hours){
        info.appendChild(el("p", "row-hours", `Today: ${hours}`));
    }
    row.appendChild(info);

    const tags = el("div", "tags");
    if(place.rating != null){
        tags.appendChild(el("span", "tag yellow", `★ ${place.rating.toFixed(1)} on Google`));
    }
    tags.appendChild(el("span", "tag", `${place.review_count.toLocaleString()} reviews`));
    tags.appendChild(statusTag(place));
    row.appendChild(tags);
    let scoreText = "–";
    if (place.score != null) {
        scoreText = place.score.toFixed(2);
    }   
    const score = el("div", "row-score");
    score.appendChild(el("span", "score-label", "MAPRANK"));
    score.appendChild(el("span", "score-value", scoreText));
    row.appendChild(score);
    return row;
}

function renderPodiumStep(place, rank){
    const step = el("div", `pod pod-${rank}`);

    const card = el("div", "pod-card box");
    card.appendChild(el("h2", "pod-name", place.name));
    const stats = [];
    if(place.rating != null){
        stats.push(`★ ${place.rating.toFixed(1)} on Google`);
    }
    if(place.score != null){
        stats.push(`MapRank ${place.score.toFixed(2)}`);
    }
    card.appendChild(el("p", "pod-stats", stats.join(" · ")));
    card.appendChild(statusTag(place));
    if(place.summary){
        card.appendChild(summaryText(place, "pod-summary"));
        let loading;
        if (place.summary == "Loading summary...") {
            loading = true;
        } else {
            loading = false;
        }
        if (!loading) {
            card.classList.add("expandable");

            let buttonText = "READ MORE ▾";
            if (place.summaryExpanded) {
                card.classList.add("expanded");
                buttonText = "SHOW LESS ▴";
            }

            const toggle = el("button", "pod-toggle", buttonText);
            toggle.type = "button";
            toggle.setAttribute("aria-expanded", String(Boolean(place.summaryExpanded)));
            card.appendChild(toggle);

            card.addEventListener("click", () => {
                place.summaryExpanded = !place.summaryExpanded;
                renderResults(results);
            });
        }
    }
    step.appendChild(card);

    step.appendChild(el("div", "pod-block", rank));
    return step;
}

function renderResults(places){
    const top3 = places.slice(0, 3);
    const rest = places.slice(3);

    podium.innerHTML = "";
    for(const rank of [2, 1, 3]){
        if(top3[rank - 1]){
            podium.appendChild(renderPodiumStep(top3[rank - 1], rank));
        }
    }

    placesId.innerHTML = "";
    rest.forEach((place, i) => {
        placesId.appendChild(renderRow(place, i + 4));
    });
}

if (placesId) {
    renderResults(results);
}
