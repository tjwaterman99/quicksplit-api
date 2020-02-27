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
		return "8b9e8424-54d9-4f7d-8013-7dfd5240d248" // production token
	} else {
		return "3103b15e-1ec0-465d-8a74-1fdfdcff40dc" // staging token
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
	// Display navbar if user  is in "experimental" cohort
	if (cohort == "experimental") {
		$(".menu").attr("hidden", false)
	}

	// and log exposure event on every page view
	quicksplit.post("/exposures", {
		"experiment": "demo-experiment",
		"cohort": cohort,
		"subject": user
	})

	// log conversion event if page stays open for 30+ seconds
	setTimeout(function() {
		quicksplit.post("/conversions", {
			"experiment": "demo-experiment",
			"subject": user
		})
	}, 30*1000)
}
$(document).ready(runSplitTest)
