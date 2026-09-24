$( document ).ready(function() {
	$( "#input_text" ).focus();

	$("#input_text").on("paste keypress", function(event){
		$('#left_button').text('Clear text');
		$('#left_button').removeClass('btn-primary');
		$('#left_button').addClass('btn-danger');
	    setTimeout(function () {
			var text = $("#input_text").val();
			$.ajax({
			  url:'https://jsahu.me/api/tools/suc',
			  type:"POST",
			  data: { input_text: text}
			}).done(function(data) {
			  $("#unicode_text").val(data.unicode);	
			});
		}, 10);
	} );

	$('#left_button').click(function(){
		$("#input_text").val('');
		$('#left_button').text('Paste your text in the below box');
		$('#left_button').removeClass('btn-danger');
		$('#left_button').addClass('btn-primary');
		$("#input_text").focus();
	});

	$('#unicode_text_button').click(function(){
		if ($('#unicode_text').val() == "") {
		  swal("Oops...There is nothing to copy!", "Please paste some text in the left box first.", "error");
		} else {
		  //select the converted text
		  $('#unicode_text').select();
		  //copy the selected text
		  document.execCommand('copy');
		  $('#unicode_text_button').text('Copied');
		  $('#unicode_text_button').removeClass('btn-primary');
		  $('#unicode_text_button').addClass('btn-success');
		  setTimeout(function(){
		  	$('#unicode_text_button').text('Click to select all and copy');
		  	$('#unicode_text_button').removeClass('btn-success');
		    $('#unicode_text_button').addClass('btn-primary');			    
		  }, 500);
		}
	});
});