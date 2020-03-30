//Frontend javascript code for the model detail page.


let solveOdeInJs = function(){
    /* Solves the ODE and plops it in the data div for the draw function to work*/
    let inputs = $('#ode-parameter-form :input');
    let parameters = {};
    inputs.each(function() {
        parameters[this.name] = $(this).val();
    });


    let tr = parameters.transmission_rate;
    let rr = parameters.recovery_rate;

    let i = parameters.initial_percent_infected / 100;
    let r = 0;
    let s = 1 - i - r;

    let susceptible_data = [s];
    let infected_data = [i];
    let recovered_data = [r];

    for(t=0; t<parameters.max_t; t++){
        let s_prime = - tr * s * i
        let i_prime = tr * s * i - rr * i
        let r_prime = rr * i

        s += s_prime
        i += i_prime
        r += r_prime

        s = Math.min(Math.max(s, 0), 1)
        i = Math.min(Math.max(i, 0), 1)
        r = Math.min(Math.max(r, 0), 1)

        susceptible_data.push(s)
        infected_data.push(i)
        recovered_data.push(r)

    }

    let data = {
        "recovered": recovered_data,
        "infected": infected_data,
        "susceptible": susceptible_data,
        "peak_infected": Math.round(100*Math.max(...infected_data)),
        "total_recovered": Math.round(100*recovered_data[infected_data.length-1])
    };


    $('#data-div').attr('data-solution', JSON.stringify(data));
    drawData();

};

let distanceLadies = function(){
    /* Socially distancing ladies */
    let d = $('#id_transmission_rate').attr('value');
    $('.socially-distant').css('margin-right', (10-d) + '%');

};

let addHospitals = function(){
    /* Adding hospitals */

    let r = $('#id_recovery_rate').attr('value');
    let s = '🏥';
    for(let i=0; i<r*10; i++){
        s += '🏥';
    }
    $('#recovery-centres').html(s);
};


let enableSaveBtn = function(){
    /* Enable the save button when an input changes */
    if($("#save-btn").hasClass("disabled")){
        bindSaveBtn();
        $("#save-btn").removeClass("disabled");
    }
};

let submitSaveForm = function(){
    let form = $("#ode-parameter-form");
    let url = form.attr('action');

    $.ajax({
           type: "POST",
           url: url,
           data: form.serialize(), // serializes the form's elements.
           success: function(resp){
                $("#save-btn").addClass("disabled");
                $('#data-div').attr('data-solution', JSON.stringify(resp));
                drawData();
           }
    });
};

let bindInputToDisplays = function(){
    /* Binds the inputs to make ladies dance and to rerender plot if applicable */

    $('#id_transmission_rate').on('input', function () {
        $(this).attr('value', this.value); //JS is weird sometimes.
          distanceLadies();
    });

    $('#id_recovery_rate').on('input', function () {
        $(this).attr('value', this.value);
        addHospitals();
        });

    $( "#ode-parameter-form input" ).on('input', function() {
        enableSaveBtn();
        if($('#auto-render').prop("checked")){
            solveOdeInJs();
        }
    });
};

let bindSaveBtn = function(){
    $("#save-btn").unbind().click( function(event) {
        event.preventDefault();
        submitSaveForm();
        });
};

let bindSimulateJsBtn = function(){
    $("#js-btn").unbind().click( function(event) {
        event.preventDefault();
        console.log("Running simulation on frontend")
        solveOdeInJs();
        console.log("Simulation finished and rendered")
        });
};

let bindSimulateDjangoBtn = function(){
    $("#django-btn").unbind().click( function(event) {

        console.log("Running simulation on backend")
        //This is basically trying to showcase using this as an external API. 
        // This is similar to standalone script showcasing the API.

        let form = $("#ode-parameter-form");
        
        // Hardcoded url, to better simulate a more external 
        // site calling this.
        let url = 'http://{{request.META.HTTP_HOST}}/solve_ode/'


        // This is a little bit of hack to make it look a little
        // bit more like a regular JSON object that would actually
        // use in an external API.
        let inputs = $('#ode-parameter-form :input');
        let parameters = {};
        inputs.each(function() {
            parameters[this.name] = $(this).val();
        });
        // Using the csrf token in the header to make the browser not complain.
        // If I was doing this for real (and using this only in a browser), I would
        // Have an entire django/forms workflow, but for the purposes of demonstration
        // I'm doing this.
        let csrfToken = parameters.csrfmiddlewaretoken
        delete parameters.csrfmiddlewaretoken;
        delete parameters.name;

        // Sending the AJAX request.
        $.ajax({
            type: "GET",
            url: url,
            contentType: 'application/json; charset=utf-8',
            processData: true,
            headers: {
                "X-CSRFToken": csrfToken 
            },
            data: parameters,
            // data: JSON.stringify(parameters),
            success: function(resp){
                $('#data-div').attr('data-solution', JSON.stringify(resp));
                drawData();
                console.log("Simulation finished and rendered")
                }
        });
    });
};

let bindSaveSvg = function(){
    $("#save-svg-btn").unbind().click( function(event) {
        // Saves the svg image to the model object.

        event.preventDefault();
        let url = $(this).attr('href');

        // Getting the csrf token, again, by no means the right
        // way of doing this, but I'm trying to get it out the door.
        let inputs = $('#ode-parameter-form :input');
        let csrfToken = inputs[0].value;
        let svgContainer = $('#svg-container')

        $.ajax({
            type: "POST",
            url: url,
            data: {html: svgContainer.html()}, // serializes the form's elements.
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function(resp){

                alert("This SVG will now be used in the rationale")
            }
        });
    });
};

let drawData = function(){
    /* Does all the d3 work and draws the plot */

    // colors = [recover color, infected color, susceptible color]
    let colors = ['#ff0000', '#3CB371', '#ffab00']

    let dataDiv = document.querySelector("#data-div");
    let data = JSON.parse(dataDiv.dataset.solution);
    let targetElement = d3.select('#svg-container');

    //Clear the html
    targetElement.html("");        

    let margin = {top: 50, right: 200, bottom: 50, left: 50}
      , width = 1200 - margin.left - margin.right
      , height = 500 - margin.top - margin.bottom;

    let n = data['recovered'].length - 1;

    let xScale = d3.scaleLinear()
        .domain([0, n])
        .range([0, width]); 

    let maximum = 1;

    let yScale = d3.scaleLinear()
        .domain([0, maximum]) 
        .range([height, 0]); 

    let line = d3.line()
        .x(function(d, i) { return xScale(i); })
        .y(function(d) { return yScale(d); })
        .curve(d3.curveMonotoneX) 

    let svg = targetElement.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr('xmlns', "http://www.w3.org/2000/svg")
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale));

    svg.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(yScale)); 

    svg.append("path")
        .datum(data['recovered'])
        .attr("class", "line") 
        .attr("d", line) 
        .attr("stroke", colors[0])
        .attr("stroke-width", 3)
        .attr("fill", 'none');
    
    svg.append("path")
        .datum(data['infected'])
        .attr("class", "line") 
        .attr("d", line) 
        .attr("stroke", colors[1])
        .attr("stroke-width", 3)
        .attr("fill", 'none');

    
    svg.append("path")
        .datum(data['susceptible'])
        .attr("class", "line") 
        .attr("d", line) 
        .attr("stroke", colors[2])
        .attr("stroke-width", 3)
        .attr("fill", 'none');

    let legendKeys = ["Recovered", "Infected", "Susceptible"];

    let lineLegend = svg.selectAll(".lineLegend").data(legendKeys)
        .enter().append("g")
        .attr("class","lineLegend")
        .attr("transform", function (d,i) {
                return "translate(" + (width-200) + "," + (100+i*20)+")";
            });

    lineLegend.append("text").text(function (d) {return d;})
        .attr("transform", "translate(15,9)"); //align texts with boxes

    lineLegend.append("rect")
        .attr("fill", function (d, i) {return colors[i]; })
        .attr("width", 10).attr("height", 10);

    svg.append("text")
        .text("Peak Infected: "+ data['peak_infected'] +"%")
        .attr("transform", "translate("+(width-400)+",120)");
        svg.append("text")
        .text("Total Recovered: "+ data['total_recovered'] +"%")
        .attr("transform", "translate("+(width-400)+",140)");

};

$(document).ready(function() { 

    bindInputToDisplays();
    distanceLadies();
    addHospitals();
    bindSimulateJsBtn();
    bindSimulateDjangoBtn();
    bindSaveSvg();
    drawData();

});