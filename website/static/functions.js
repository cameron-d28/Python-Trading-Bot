function cycle_mySQL(){

	var image = document.getElementById("upward_arrow");
	image.style.display = 'none';
	var arrow_header = document.getElementById("arrow_header");
	arrow_header.innerHTML = 'Working on Trades Now';

    //Sets up the AJAX object
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
		//if we're actually done successfully
		if (this.readyState == 4 && this.status == 200) {
		   //update the text to say the new number of likes
		   	var arrow_header = document.getElementById("arrow_header");
			arrow_header.innerHTML = 'Trades Complete';
		   
		   //this.responseText is a variable which contains the return value
		   //from Python
		}
    };
    //run the python code to send order and return:
    //  Order number, Ticker, and Method Used for Order

    //Tells JS which website to go to and
	//how to go to it (GET or POST)
	xhttp.open("POST", "/cycle_mySQL", true);
	
	//Starts the AJAX request
    xhttp.send(); //asynchronous request

    //update Database
}