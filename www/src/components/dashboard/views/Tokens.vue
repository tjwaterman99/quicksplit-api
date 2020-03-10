<template>
	<div class="tokens">
		<h1>Tokens</h1>
		<ul class="nav nav-tabs">
			<li class="nav-item">
				<a href="#" class="nav-link staging" v-bind:class="{active: staging}" @click="activate">Staging</a>
			</li>
			<li class="nav-item">
				<a href="#" class="nav-link production" v-bind:class="{active: !staging}" @click="activate">Production</a>
			</li>
		</ul>
		<ul class="list-group">
			<li class="list-group-item" v-for="token in displayTokens" :key="token.id">
				<b>{{displayPublishableName(token.private)}} token:</b> {{token.value}}
			</li>
		</ul>
	</div>
</template>


<script>
export default {
	name: "Tokens",
	data: function() {
		return {
			staging: true
		}
	},
	computed: {
		tokens: function() {
			if (this.$api.user) {
				return this.$api.user.tokens
			} else {
				return []
			}
		},
		displayTokens: function() {
			if (this.staging) {
				return this.tokens.filter(token => token.environment == "staging")
			} else {
				return this.tokens.filter(token => token.environment == "production")
			}
		}
	},
	created: function() {
		if (!this.tokens) {
			var that = this;
			this.$api.get('/tokens').then(function(resp) {
				that.tokens = resp.data.data
			}).catch(function(err) {
				console.log(err)
			})
		}
	},
	methods: {
		activate: function(event) {
			console.log(event.target.className)
			if (event.target.className.match("active")) {
				return
			} else {
				this.staging = !this.staging
			}
		},
		displayPublishableName: function(publishable) {
			if (publishable) {
				return "Public"
			} else {
				return "Private"
			}
		}
	}
}
</script>

<style lang="scss" scoped=true>

@import "src/assets/scss/variables.scss";

.nav-link {
	border-color: $primary;
	margin-right: 0.25em;
}

.nav-link:hover {
	border-color: $primary !important;
}

.nav-link.active {
	background-color: $primary;
	border-color: $primary;
	color: $white;
}

.nav-tabs {
	border-color: $primary;
}
</style>
