<template>
	<nav class="navbar navbar-expand-lg navbar-light">
		<div class="container">
		<a class="navbar-brand" href="/">
			<img src="/logo.png" width="30" height="30" class="d-inline-block align-top" alt="" />
			Quick Split
		</a>

		<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
		<span class="navbar-toggler-icon"></span>
		</button>

		<div class="collapse navbar-collapse" id="navbarSupportedContent">
		<ul class="navbar-nav mr-auto">
		<li class="nav-item">
		<router-link class="nav-link" to="/faq">FAQ</router-link>
		</li>
		<li class="nav-item">
		<router-link class="nav-link" to="/get-started">Get Started</router-link>
		</li>
		<li class="nav-item">
		<router-link class="nav-link" to="/contact">Contact</router-link>
		</li>
		</ul>

		<ul class="navbar-nav ml-auto" v-if="loggedOut">
			<li class="nav-item">
				<router-link class="nav-link" to="/login">Log In</router-link>
			</li>
		</ul>

		<ul class="navbar-nav ml-auto" v-else>
			<li class="nav-item">
				<a class="nav-link" href="/" @click="logOut">Log out</a>
			</li>
			<li class="nav-item">
				<router-link to="/dashboard" class="nav-link">Dashboard</router-link>
			</li>
		</ul>
		</div>
		</div>
	</nav>
</template>

<script>
export default {
	name: "NavBar",
	computed: {
		loggedOut: function() {
			return this.$api.user == null
		}
	},
	methods: {
		logOut: function() {
			return this.$api.logout()
		}
	}
}
</script>

<style lang="scss">

@import "src/assets/scss/variables.scss";

.menu {
	background-color: $gray-800;
	text-align: center;
  color: #FFFFFF;
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
