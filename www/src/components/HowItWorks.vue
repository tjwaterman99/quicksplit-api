<template>
	<!-- FEATURES
	================================================== -->
	<section class="py-8 py-md-11 border-bottom">
		<div class="container">
			<div class="row justify-content-center">
				<div class="col-12 col-md-10 col-lg-8 text-center">

					<!-- Heading -->
					<h2>
						How it works
					</h2>

					<!-- Text -->
					<p class="font-size-lg text-muted mb-7 mb-md-9">
						Quick Split is built on a resource-based, restful web API. If your application can log data, you can run a rigorous, statistically valid A/B test with just two web requests.
					</p>

				</div>
			</div> <!-- / .row -->
			<div class="row">
				<div class="col-12 col-md-4" data-aos="fade-up">
					<!-- Icon -->
					<!-- <div class="icon text-primary mb-3">
						@@include("assets/img/icons/duotone-icons/General/Settings-1.svg")
					</div> -->

					<!-- Heading -->
					<h4 class="text-center">
						Log when a user sees your A/B test
					</h4>

					<!-- Text -->
					<p class="mb-6 mb-md-0 px-3">
						<img src="@/assets/img/code-exposures-v2.svg" class="img-fluid screenshot">
					</p>

				</div>
				<div class="col-12 col-md-4" data-aos="fade-up" data-aos-delay="50">


					<!-- Heading -->
					<h4 class="text-center">
						Log when they convert
					</h4>

					<!-- Text -->
					<p class="mb-6 mb-md-0 px-3">
						<img src="@/assets/img/code-conversions-v2.svg" class="img-fluid screenshot">
					</p>

				</div>
				<div class="col-12 col-md-4" data-aos="fade-up" data-aos-delay="100">

					<!-- Heading -->
					<h4 class="text-center">
						Get results via dashboard or API
					</h4>

					<!-- Text -->
					<p class="mb-6 mb-md-0 px-3">
						<img src="@/assets/img/code-get-results-v2.svg" class="img-fluid screenshot">
					</p>

				</div>
			</div> <!-- / .row -->
		</div> <!-- / .container -->
	</section>

	<!-- <h3 class="text-center"> How it works </h3>
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
	</div> -->

</template>


<script>
export default {
	name: "HowItWorks"
}
</script>

<style lang="scss" scoped=true>
</style>
