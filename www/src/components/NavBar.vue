<template>
	<div class="container-fluid menu">
		<div class="row">
			<div class="container">
				<div class="col">
					<span><a href="#faq">FAQ</a></span>
					<span><a href="#contact">Contact</a></span>
					<span><a href="#get-started">Get started</a></span>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "NavBar",
	props: {}
}
</script>

<style lang="scss">

@import "../assets/scss/styles.scss";

.menu {
	background-color: $gray-800;
	text-align: center;
  color:#FFFFFF;
  padding-top: 1em;
  font-size: 0.8em;
}
.menu span {
  padding: 1em;
}

.menu span a {
  color: #EAF5FF;
}
</style>
