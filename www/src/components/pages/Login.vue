<template>
	<div>
		<Header>Log in</Header>
		<div class="container">
		<div class="row">
			<div class="col-md-6 offset-md-3">
				<form>
				<div class="form-group">
				<label for="email">Email address</label>
					<input v-model="email" type="email" class="form-control" id="email" aria-describedby="emailHelp" placeholder="Enter email" autofocus=true>
					<small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small>
				</div>
				<div class="form-group">
					<label for="password">Password</label>
					<input v-model="password" type="password" class="form-control" id="password" placeholder="Password">
				</div>
				<button v-on:click="login" type="submit" class="btn btn-primary btn-block">Submit</button>
				</form>
				<div class="alert alert-danger" v-if="error">{{ error }}</div>
				<div class="alert alert-success" v-if="success">{{ success }}</div>
			</div>
		</div>
	</div>
</div>
</template>

<script>

import Header from '../Header';

export default {
	name: "Login",
	components: {
		"Header": Header
	},
	data: function() {
		return {
			email: null,
			password: null,
			error: null,
			success: null
		}
	},
	methods: {
		login: function(event) {
			event.preventDefault()
			var self = this
			this.$api.login({
				email: this.email,
				password: this.password
			}).then(function(resp) {
				self.success = "Succesfully logged in. Redirecting now..."
				self.resp = resp
				setTimeout(function() {self.$router.push('/')}, 1000)
			}).catch(err => {
				console.log(err)
				self.error = err.response.data.message
			})
		}
	}
}
</script>

<style scoped=true lang="scss">
form {
	margin-top: 2em;
	margin-bottom: 1em;
}
</style>
