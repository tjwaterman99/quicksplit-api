<template>
	<div class="container-fluid marquee">
		<div class="row">
			<div class="col-sm-12">
				<img class="logo" src="/logo.png"></img>
				<h1>Quick Split</h1>
				<h2>The developer tool for fast A/B tests</h2>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "Marquee",
	props: {}
}
</script>

<style lang="scss">

@import "../assets/scss/variables.scss";

.marquee {
  background-color: $gray-800;
  text-align: center;
  padding-bottom: 2em;
  padding-top: 1em;
  color: #FFFFFF;
}

.logo {
  max-height: 15em;
  max-width: 15em;
  margin-bottom: 1em;
}
</style>
