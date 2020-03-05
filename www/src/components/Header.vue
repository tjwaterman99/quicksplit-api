<template>
	<div class="container-fluid">
		<div class="row">
			<div class="col">
				<h1>
					<slot></slot>
				</h1>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "Header"
}
</script>

<style lang="scss" scoped=true>

@import "src/assets/scss/variables.scss";

.row {
	background-color: $gray-800;
	text-align: center;
	color: white;
	padding-top: 3em;
	padding-bottom: 3em;
}
</style>
