function methodVerify(){
	var msg = "";
	
	var form = document.getElementById('profile-select');
	var choice = document.getElementById('profile-selection');
	if( choice.value == 'profile_add' ){
		form.method = "GET";
		form.action = "/thermostat/profile_create";
		choice.value = "";
	};

//	console.log(msg)
	return 0;
}

function addSchedule(){

	var entry = [];
	var i = 0;
	entry[i] =	'<form method="POST">'; ++i;
	entry[i] =		'<span>Target: </span>'; ++i;
	entry[i] = 		'<input name="schedule_target" type="text">'; ++i;
	entry[i] = 		'<span>&deg;C</span> <br>'; ++i;
	entry[i] =		'<span>Start time: </span>'; ++i;
	entry[i] =		'<input name="schedule_hour" type="text" maxlength="2">'; ++i;
// Tag for hour/minute delimiter?
	entry[i] = 		':<input name="schedule_minute" type="text" maxlength="2"> <br>'; ++i;
	entry[i] =		'<input type="submit" value="Enter">'; ++i;
	entry[i] =	'</form>';

	var schedlist = document.getElementById('schedule-list');
	var item = document.createElement('li');
	item.innerHTML = entry.join("");
	schedlist.appendChild(item);
	
// Temporary solution until multiple additions are implemented
	var button = document.getElementById('add-schedule');
	(button.parentNode).removeChild(button);

//	console.log(msg);
	return 0;
}

var schedule_count = 0;
function initSchedule(){

	var entry = [];
	var i = 0;
	entry[i] =  '<span>Target: </span>'; ++i;
	entry[i] = 	'<input name="new_schedule_target' + schedule_count + '" type="text">'; ++i;
	entry[i] = 	'<span>&deg;C</span> <br>'; ++i;
	entry[i] =	'<span>Start time: </span>'; ++i;
	entry[i] =	'<input name="new_schedule_hour' + schedule_count + '" type="text" maxlength="2">'; ++i;
// Tag for hour/minute delimiter?
	entry[i] = 		':<input name="new_schedule_minute' + schedule_count + '" type="text" maxlength="2"> <br>'; ++i;

	var schedlist = document.getElementById('new-schedule-list');
	var item = document.createElement('li');
	item.innerHTML = entry.join("");
	schedlist.appendChild(item);
	schedule_count++;	

	return 0;
}
