<template>
	<div>
	<Marquee />
	<HowItWorks />
	</div>
</template>

<script>
import Marquee from '../Marquee';
import HowItWorks from 'components/HowItWorks';

export default {
	name: "Home",
	components: {
		'Marquee': Marquee,
		'HowItWorks': HowItWorks,
	}
}
</script>

<style lang="scss">
h3 {
	margin-top: 1em;
	font-size: 2em;
}

.last-cta {
	margin-bottom: 3em;
}
</style>
