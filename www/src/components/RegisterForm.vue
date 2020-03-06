<template>
<div>
<form class="register-form">
	<div class="form-group">
	<label class="text-dark" for="exampleInputEmail1">Email address</label>
	<input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" placeholder="Enter email" autofocus=true v-model="email">
	<small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small>
	</div>

	<div class="form-group">
	<label class="text-dark"  for="exampleInputPassword1">Password</label>
	<input type="password" class="form-control" id="exampleInputPassword1" placeholder="Password" v-model="password">
	</div>
	<button type="submit" class="btn btn-primary btn-block btn-lg font-weight-bold" @click="onClick">Sign Up for Quick Split</button>
	<div class="alert alert-danger" v-if="error">{{ error }}</div>
	<div class="alert alert-success" v-if="success">{{ success }}</div>
</form>
</div>
</template>

<script>
export default {
	name: "RegisterForm",
	data: function() {
		return {
			password: null,
			email: null,
			success: null,
			error: null
		}
	},
	methods: {
		onClick: function(event) {
			event.preventDefault()
			var self  =  this
			this.$api.register({
				email: this.email,
				password: this.password
			}).then(resp => {
				self.success = "Succesfully created account. Redirecting now..."
				self.resp = resp
				setTimeout(function() {self.$router.push('/get-started')}, 1000)
			}).catch(err => {
				self.error = err.response.data.message
			})
		}
	}
}
</script>

<style scoped=true lang="scss">

@import "src/assets/scss/variables";

.register-form {
	background-color: $white;
	padding:  1.5em;
	border-radius: 0.5em;
}

.alert {
	margin-top: 1em;
}
</style>
