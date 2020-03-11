<template>
	<div v-if="this.$api.user">
		<ul class="list-group">
			<li class="list-group-item">
				<b>Email: </b> {{ this.$api.user.email }}
			</li>
			<li class="list-group-item">
				<b>Account ID: </b> {{ this.$api.user.account.id }}
			</li>
			<li class="list-group-item">
				<b>Plan: </b> {{ this.$api.user.account.plan.name }}
			</li>
		</ul>
	</div>
</template>

<script>
export default {
	name: "Account"
}
</script>

<style lang="scss" scoped=true>
</style>
