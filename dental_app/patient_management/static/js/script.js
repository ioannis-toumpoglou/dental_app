$(document).ready(function(){
	$('a[data-bs-toggle="tab"]').on('show.bs.tab', function(e) {
		localStorage.setItem('activeTab', $(e.target).attr('href'));
	});
	var activeTab = localStorage.getItem('activeTab');
	if(activeTab){
		$('#nav-tab a[href="' + activeTab + '"]').tab('show');
	}
	$('.nav-tabs').show();
});

function clearOdontogramColor() {
    document.getElementById('odontogram-outer-color-options').selectedIndex = 0;
}

function selectOdontogramColor() {
    let sectionNumber = document.getElementById("odontogram-outer-top-view-selection").value;
    console.log(sectionNumber);
    let color = document.getElementById("odontogram-outer-color-options").value;
    console.log(color);

    if (color == "") {
        document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-black`).style.opacity = "0";
        document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-brown`).style.opacity = "0";
        document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-yellow`).style.opacity = "0";
    }

    let elementName = `odontogram-outer-top-view-image-${sectionNumber}-${color}`;
    console.log(elementName);

    if (sectionNumber && color) {
        if (color == "black") {
            document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-brown`).style.opacity = "0";
            document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-yellow`).style.opacity = "0";
        } else if (color == "brown") {
            document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-black`).style.opacity = "0";
            document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-yellow`).style.opacity = "0";
        } else if (color == "yellow") {
            document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-black`).style.opacity = "0";
            document.getElementById(`odontogram-outer-top-view-image-${sectionNumber}-brown`).style.opacity = "0";
        }
        document.getElementById(elementName).style.opacity = "1";
    }
}

function clearOuterTopViewModalData() {
    for (let sectionNumber=1; sectionNumber <= 5; sectionNumber++) {
        let blackElementName = `odontogram-outer-top-view-image-${sectionNumber}-black`;
        let brownElementName = `odontogram-outer-top-view-image-${sectionNumber}-brown`;
        let yellowElementName = `odontogram-outer-top-view-image-${sectionNumber}-yellow`;

        document.getElementById(blackElementName).style.opacity = "0";
        document.getElementById(brownElementName).style.opacity = "0";
        document.getElementById(yellowElementName).style.opacity = "0";
        document.getElementById('odontogram-outer-top-view-selection').selectedIndex = 0;
        document.getElementById('odontogram-outer-color-options').selectedIndex = 0;
    }
}