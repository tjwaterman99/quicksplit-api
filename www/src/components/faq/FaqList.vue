<template>

	<div class="row faq-list">
	<p class="anchor" id="faq"></p>
	<div class="col-12 col-lg-8 offset-lg-2">
	<div class="section faq">
	<h2 class="text-center">Frequently asked questions</h2>
	<br>
	<p class="faq-question"><b>Q: What sample sizes can I use for a single experiment?</b></p>
	<p>You can log up to <b>3,000 subjects</b> in a single experiment. In typical situations, that's a large enough sample size to detect ~1% differences in conversion rates.<p>
	<hr>
	<p class="faq-question"><b>Q: Can I run multiple experiments at the same time?</b></p>
	<p>You can run up to <b>three concurrent experiments</b> on a single account. To stop an existing experiment, use the command <code>quicksplit stop</code>. To restart an experiment, use the command <code>quicksplit start</code>.<p>
	<hr>
	<p class="faq-question"><b>Q: Can I do a three-way test (an A/B/C test)?</b></p>
	<p>You can use any number of cohorts for your experiment, including running three way tests.<p>
	<hr>
	<p class="faq-question"><b>Q: How do you calculate whether my experiment is statistically significant?</b></p>
	<p>We use the industry-standard methodology called an <b><a href="https://en.wikipedia.org/wiki/Analysis_of_variance">ANOVA</a></b> test. If the F-statistic of the ANOVA test has an associated p-value of less than 0.1, we conclude that the test is significant.<p>
	<hr>
	</div>
	</div>
	</div>
</template>

<script>
export default {
	name: 'FaqList',
	props: {}
}

</script>

<style>
</style>
