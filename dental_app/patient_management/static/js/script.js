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