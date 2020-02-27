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

	var user = getUser();
	var cohort = getCohort();
	var token = getToken();
	var quicksplit = axios.create({
		baseURL: "https://api.quicksplit.io",
		headers: {
			"Authorization": token,
			"Content-Type": "application/json"
		}
	})
	// TODO: display navbar if user  is in "experimental" cohort
	// and log exposure & conversion events

$(document).ready(runSplitTest)
