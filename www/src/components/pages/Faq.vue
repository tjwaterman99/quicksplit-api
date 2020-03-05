<template>
	<div>
	<Header>Frequently Asked Questions</Header>
	<FaqList />
	</div>
</template>

<script>
import FaqList from '../faq/FaqList';
import Header from '../Header';

export default {
	name: "Faq",
	components: {
		'FaqList': FaqList,
		'Header': Header
	}
}
</script>

<style lang="scss">
</style>
