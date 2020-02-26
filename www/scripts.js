function getUser() {
	var user_id = localStorage.getItem('user_id');
	if (!user_id) {
		user_id = Math.random() * 1e20
		localStorage.setItem('user_id', user_id)
	}
	return user_id
}

function getCohort() {
	var cohort = localStorage.getItem('cohort');
	if (!cohort) {
		if (Math.random() < 0.5) {
			cohort = "experimental"
		} else {
			cohort = "control"
		}
		localStorage.setItem('cohort', cohort)
	}
	return cohort
}

function getToken() {
	if (window.location.href.startsWith('https://www.quicksplit.io')) {
		return "a79c5d0b-9d8f-4507-adbe-ab2d8dc2bfb2" // production token
	} else {
		return "cc625d41-9dba-4e9a-8515-a63a28581d8f" // staging token
	}
}

function runSplitTest() {
	console.log("User: ", getUser())
	console.log("Cohort: ", getCohort())
	console.log("Public token: ", getToken())

	$.post({
		method: 'POST',
		url: "https://api.quicksplit.io/exposures",
		headers: {
			Authorization: getToken()
		},
		contentType: "application/json; charset utf-8",
		data: JSON.stringify({
			experiment: "demo-experiment",
			cohort: getCohort(),
			subject: getUser()
		})
	})

	if (getCohort() == "control") {
		$('.menu').attr("hidden", true)
	}

	setTimeout(function() {
		$.post({
			method: 'POST',
			url: "https://api.quicksplit.io/conversions",
			headers: {
				Authorization: getToken()
			},
			contentType: "application/json",
			data: JSON.stringify({
				subject: getUser(),
				experiment: "demo-experiment"
			})
		})
	}, 30 * 1000)
}

$(document).ready(runSplitTest)
