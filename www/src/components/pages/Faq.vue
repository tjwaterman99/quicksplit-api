<template>
	<div>
	<Header>Frequently Asked Questions</Header>
	<FaqList />
	</div>
</template>

<script>
import FaqList from '@/components/faq/FaqList';
import Header from '@/components/Header';

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
