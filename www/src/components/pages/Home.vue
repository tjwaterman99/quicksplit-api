<template>
	<div>
	<Marquee />
	<h3 class="text-center"> How it works </h3>
	<div class="container">
		<div class="row">
			<div class="col-lg-4">
				<Card header="1. Log an exposure">
					<pre>
POST /exposures {
  experiment: "my-experiment",
  subject: "user-42",
  cohort: "experimental"
}</pre>
				</Card>
			</div>
			<div class="col-lg-4">
				<Card header="2. Log a conversion">
				<pre>
POST /conversions {
  experiment: "my-experiment",
  subject: "user-42"
}</pre>
				</Card>
			</div>
			<div class="col-lg-4">
				<Card header="3. Get your results">
					<pre>
GET /results {
  experiment: "my-experiment"
}</pre>
				</Card>
			</div>
		</div>
		<div class="row">
			<div class="col-sm-12 text-center">
				<a class="btn btn-primary btn-lg last-cta" href="/get-started">Get started</a>
			</div>
		</div>
	</div>
	</div>
</template>

<script>
import Marquee from '../Marquee';
import Card from '../Card';

export default {
	name: "Home",
	components: {
		'Marquee': Marquee,
		'Card': Card
	}
}
</script>

<style lang="scss">
h3 {
	margin-top: 1em;
	font-size: 2em;
}

.last-cta {
	margin-bottom: 3em;
}
</style>
