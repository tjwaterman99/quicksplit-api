<template>
	<div>
	<Header>Contact</Header>
	<div class="container">
		<div class="row">
			<div class="col-lg-8 offset-lg-2">
				<p>You can <a href="mailto:tjwaterman99@gmail.com">email us</a> with any questions or issues. Thanks for trying out <code>quicksplit</code>!</p>
			</div>
		</div>
	</div>
	</div>
</template>

<script>

import Header from "../Header"


export default {
	name: "Contact",
	components: {
		"Header": Header
	}
}
</script>

<style lang="scss" scoped=true>

p {
	margin-top: 2em;
}

</style>
