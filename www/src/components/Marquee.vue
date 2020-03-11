<template>
	<div class="container-fluid marquee">
		<div class="row">
			<div class="col-sm-12 col-md-5 offset-md-1 text-center text-md-left">
				<h1>Drive your product</h1>
				<p class="sub-header">Quick Split is the fastest, easiest way to run A/B tests on any of your products. You can A/B test a new feature in as little as 3 lines of code, without needing a data scientist.</p>
			</div>
			<div class="col-sm-12 col-md-4 offset-md-1">
				<RegisterForm />
			</div>
		</div>
	</div>
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

.marquee {
  background-color: $gray-800;
  padding-bottom: 3em;
  padding-top: 5em;
  color: #FFFFFF;

	h1 {
		font-size: 3em;
	}

	p {
		margin-top: 2em;
		font-size: 1.25em;
		color: $gray-500;
	}
}

.logo {
  max-height: 7em;
  max-width: 7em;
  margin-bottom: 1.5em;
	margin-top: 1.5em;
}
</style>
