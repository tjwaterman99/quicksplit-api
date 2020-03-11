<template>
	<div class="dashboard-nav">
		<ul>
			<li>
				<router-link to="/dashboard">Experiments</router-link>
			</li>
			<li>
				<router-link to="/get-started">Get Started</router-link>
			</li>
			<li>
				<router-link to="/payments">Payments</router-link>
			</li>
			<li>
				<router-link to="/dashboard/account">Account</router-link>
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
