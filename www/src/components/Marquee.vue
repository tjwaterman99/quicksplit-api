<template>
	<section class="pt-4 pt-md-11">
		<div class="container">
			<div class="row align-items-center">
				<div class="col-12 col-md-5 col-lg-6 order-md-2">

					<RegisterForm />


				</div>
				<div class="col-12 col-md-7 col-lg-6 order-md-1" data-aos="fade-up">

					<!-- Heading -->
					<h1 class="display-3 text-center text-md-left">
						Drive your <span class="text-primary"><b>product</b></span>.
					</h1>

					<!-- Text -->
					<p class="lead text-center text-md-left text-muted mb-6 mb-lg-8">
						Quick Split is the fastest, easiest way to run A/B tests on any of your products. You can A/B test a new feature in as little as 3 lines of code, without needing a data scientist.
					</p>

					<!-- Buttons -->
					<div class="text-center text-md-left">
						<!-- <a href="overview.html" class="btn btn-primary shadow lift mr-1">
							View all pages <i class="fe fe-arrow-right d-none d-md-inline ml-3"></i>
						</a>
						<a href="docs/index.html" class="btn btn-primary-soft lift">
							Documentation
						</a> -->
					</div>

				</div>
			</div> <!-- / .row -->
		</div> <!-- / .container -->
	</section>


	<!-- <div class="container marquee">
		<div class="row">
			<div class="col-sm-12 col-md-5 offset-md-1 text-center text-md-left">
				<h1>Drive your product</h1>
				<p class="sub-header">Quick Split is the fastest, easiest way to run A/B tests on any of your products. You can A/B test a new feature in as little as 3 lines of code, without needing a data scientist.</p>
			</div>
			<div class="col-sm-12 col-md-4 offset-md-1">
				<RegisterForm />
			</div>
		</div>
	</div> -->
</template>

<script>
import RegisterForm from '@/components/RegisterForm';

export default {
	name: "Marquee",
	components: {
		'RegisterForm': RegisterForm
	}
}
</script>

<style lang="scss">

@import "@/assets/scss/variables.scss";

</style>
