<template>


	<div class="row">
		<p class="anchor" id="get-started"></p>
	<div class="col-12 col-lg-8 offset-lg-2">
	<div class="section">
	<h3>Register an account</h3>
	<hr>
	<p>Download the CLI (requires Python3.7+ and pip installed on your system).</p>
	<pre>
	$ pip install --user quicksplit
	</pre>
	<p>Register a new account.</p>
	<pre>
	$ quicksplit register
	</pre>
	<p>You'll be prompted for an email address and password. (We promise never to send you unhelpful marketing emails).</p>
	<p>Create an experiment.</p>
	<pre>
	$ quicksplit create landing-page-test
	</pre>
	<p>You'll use the name of the experiment in the next steps, where you'll log exposure and conversion events for the experiment.<p>
	<p>But before you can log events, you'll need to locate the <i><b>public, staging</b></i> token for your account.</p>
	<pre>
	$ export TOKEN=$(quicksplit tokens --staging --public)
	</pre>

	<p><b>Public</b> tokens provide for limited access to your account, only allowing logging events. They should always be used in client-side applications such as a JavaScript web app.</p>
	<p><b>Staging</b> tokens are used to separate staging data from production data. They should be used in your development environment.</p>
	<br>
	<h3>Log an exposure event</h3>
	<hr>
	<p>Log an <i>exposure</i> for your experiment by sending JSON encoded data to the <code>/exposures</code> route.</p>
	<pre>
	$ curl https://api.quicksplit.io/exposures \
	-H "Authorization: ${TOKEN}" \
	-H "Content-Type: application/json" \
	-d '{
		"experiment": "landing-page-test",
		"subject": 12345,
		"cohort": "control"
	}'
	</pre>
	<p>Exposures have three required fields: experiment, subject, and cohort.
	<ul>
	<li><code>experiment</code> is the name of the experiment you created previously. In this case, it's <code>landing-page-test</code></li>
	<li><code>subject</code> is typically a user id provided by your own backend.</li>
	<li><code>cohort</code> corresponds to which version of your application the user is experiencing. In an A/B test, you might use the labels "experimental" and "control" for your cohorts.</li>
	</ul>
	</p>

	<br>
	<h3>Log a conversion event</h3>
	<hr>
	<p>Log a <i>conversion</i> for your experiment by sending JSON encoded data to the <code>/conversions</code> route.</p>
	<pre>
	$ curl https://api.quicksplit.io/conversions \
	-H "Authorization: " \
	-H "Content-Type: application/json" \
	-d '{
		"experiment": "landing-page-test",
		"subject": 12345
	}'
	</pre>


	<p>Confirm that the exposure and conversion logging was successful by checking the recent events.</p>

	<pre>
	$ quicksplit recent --staging

	┌────────────┬───────────────────┬─────────┬─────────┬───────┬───────────────────────────────┐
	│ Type       │ Experiment        │ Subject │ Cohort  │ Value │ Last seen                     │
	├────────────┼───────────────────┼─────────┼─────────┼───────┼───────────────────────────────┤
	│ conversion │ landing-page-test │ 12345   │ control │       │ Tue, 25 Feb 2020 21:37:52 GMT │
	│ exposure   │ landing-page-test │ 12345   │ control │       │ Tue, 25 Feb 2020 21:34:35 GMT │
	└────────────┴───────────────────┴─────────┴─────────┴───────┴───────────────────────────────┘
	</pre>

	<p>Note that we used the special <code>--staging</code> flag to retrieve recent staging events. Omitting that flag would pull recent production events instead.</p>

	<br>
	<h3>Download the results of your experiment</h3>
	<hr>

	<p>You can retrieve the statistical significance of your experiment as soon as it has started receiving events.</p>

	<pre>
	$ quicksplit results landing-page-test --staging

	┌─────────┬──────────┬─────────────────┬────────────────────┐
	│ Cohort  │ Subjects │ Conversion rate │ 95% conf. interval │
	├─────────┼──────────┼─────────────────┼────────────────────┤
	│ control │ 1        │ 1               │ [,]                │
	└─────────┴──────────┴─────────────────┴────────────────────┘
	Your test is not statistically significant. Either you need to collect more data, or there is no difference in means between the cohorts
	</pre>

	<p>Note that we're using the <code>--staging</code> flag here again because we've been using the staging token.</p>

	</div>
	</div>
	</div>
</template>

<script>

export default {
	name: 'GetStarted',
	props: {}
}

</script>

<style>
</style>
