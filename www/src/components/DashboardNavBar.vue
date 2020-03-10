<template>
	<div class="dashboard-nav">
		<ul>
			<li>
				<a href="/dashboard">Quick Split</a>
			</li>
			<li>
				<a href="/get-started">Get Started</a>
			</li>
			<li>
				<a href="/payments">Payments</a>
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
