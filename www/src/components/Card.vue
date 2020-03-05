<template>
	<div class="card border-light">
		<div class="card-body">
			<h4 class="card-title text-center">{{ header }} </h4>
			<p class="card-text">
				<slot></slot>
			</p>
		</div>
	</div>
</template>


<script>
export default {
	name: "Card",
	props: {
		header: null,
		body: null
	}
}
</script>

<style lang="scss" scoped=true>

.card {
	margin-top: 1em;

	.card-body {
		padding-left: 0rem;
		padding-right: 0rem;
	}
}

</style>
