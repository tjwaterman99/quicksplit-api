<template>
	<div class="dashboard-nav">
		<ul>
			<li>
				<router-link to="/dashboard">Experiments</router-link>
			</li>
			<li>
				<a href="/get-started">Get Started</a>
			</li>
			<li>
				<a href="/payments">Payments</a>
			</li>
			<li>
				<router-link to="/dashboard/tokens">Tokens</router-link>
			</li>
		</ul>
	</div>
</template>

<script>
export default {
	name: "DashboardNavBar"
}
</script>

<style lang="scss" scoped=true>

@import 'src/assets/scss/variables.scss';

.dashboard-nav {
	background-color: #E4E8EE;

	ul {
		list-style-type: none;

		li {
			padding: 0.25em;
		}

	}
}
</style>
