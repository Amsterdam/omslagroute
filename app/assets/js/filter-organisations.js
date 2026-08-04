var selectedTags = new Array();
document.addEventListener('click', function (e) {
var button = e.target;
    
// if we clicked something that is not a tag button, get out
if (!button.hasAttribute('data-highlight-org')) return;
var filter = button.getAttribute('data-highlight-org');
filterTag(filter);
button.blur();

    function filterTag(filter) {
        var stepsContainer = document.querySelector(".section--timeline");
        // if the filter appears in the array, add classes and highlight all occurrences

        if (selectedTags.indexOf(filter) == -1) {
            button.classList.add("button--tag--selected");
            selectedTags.push(filter);
            stepsContainer.classList.add("section--timeline--filtering");
            var steps = document.querySelectorAll('[data-tags*="' + filter + '"]');

            for (var i = 0; i < steps.length; i++) {
                steps[i].classList.add("details-wrapper--highlighted");
            }

            var tags = document.querySelectorAll('[data-highlight-org*="' + filter + '"]');

            for (var i = 0; i < tags.length; i++) {
                tags[i].classList.add("button--tag--selected");
            }
        } else {
            // if we click to disable filtering of an organisation...
            button.classList.remove("button--tag--selected");

            // remove the organisation from the array
            var found = selectedTags.indexOf(filter);
            while (found !== -1) {
                selectedTags.splice(found, 1);
                found = selectedTags.indexOf(filter);
            }

            // if this was the last organisation filter to be toggled off, 
            // turn off filtering mode
            if (selectedTags.length === 0) {
                stepsContainer.classList.remove("section--timeline--filtering");
            }

            // remove all the highlights from the organisation tags ('pills')
            var tags = document.querySelectorAll('[data-highlight-org*="' + filter + '"]');
            for (var i = 0; i < tags.length; i++) {
                tags[i].classList.remove("button--tag--selected");
            }
        
            var steps = document.querySelectorAll('[data-tags*="' + filter + '"]');

            for (var i = 0; i < steps.length; i++) {
                // loop through every step which has the organisation in the data-attribute
                // and create an array out of the organisations linked to the step
                var dataTags = steps[i].getAttribute("data-tags").split(" ");
                // remove empty strings from the array
                dataTags = dataTags.filter(Boolean);

                var currentStepStillHasActivatedTags = dataTags.some(function (val) {
                    return selectedTags.indexOf(val) !== -1;
                });

                if (currentStepStillHasActivatedTags) {
                    // keep this step highlighted
                } else {
                    steps[i].classList.remove("details-wrapper--highlighted");
                }
            }
        }
    }
});