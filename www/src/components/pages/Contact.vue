<template>
	<div>
	<Header>Contact</Header>
	<div class="container">
		<div class="row">
			<div class="col-lg-6 offset-lg-3">
				<div class="alert alert-success"  v-if="!showForm">
					Thanks for contacting us. We'll reach out to {{ this.email }} shortly.
				</div>

				<div class="alert alert-danger"  v-if="errors">
					{{ errors }}
				</div>
				<form class="contact-form" v-if="showForm">
					<p>You can use the form below to contact us with any questions or issues. Thanks for trying out quicksplit.</p>
					<div class="form-group">
						<label class="text-dark" for="email-input">Email address</label>
						<input type="email" class="form-control" id="email-input" placeholder="email" autofocus=true v-model="email" required=true/>
						<small id="emailHelp" class="form-text text-muted">We'll reply to the email address you provide.</small>
					</div>
					<div class="form-group">
						<label class="text-dark" for="subject-input">Subject</label>
						<input type="text" class="form-control" id="subject-input" required
						v-model="subject" />
					</div>

					<div class="form-group">
						<label class="text-dark" for="message-input">Message</label>
						<textarea rows="6" class="form-control" id="message-input" required
						v-model="message" />
					</div>

					<div class="form-group">
						<button type="submit" class="btn btn-primary btn-block" @click="handleSubmit">Send message</button>
					</div>

				</form>
			</div>
		</div>
	</div>
	</div>
</template>

<script>

import Header from "components/Header"


export default {
	name: "Contact",
	components: {
		"Header": Header
	},
	methods: {
		loadEmail: function() {
			if (this.$api.user) {
				return this.$api.user.email
			} else {
				return null
			}
		},
		handleSubmit: function(event) {
			event.preventDefault()
			var self = this
			this.$api.post('/contacts', {
				email: self.email,
				subject: self.subject,
				message: self.message
			}).then( () => {
				self.showForm = false
				self.errors = null
			}).catch(err => {
				self.errors = err.response.data.message
			})
		}
	},
	data: function() {
		return {
			email: this.loadEmail(),
			subject: null,
			message: null,
			showForm: true,
			errors: null
		}
	}
}
</script>

<style lang="scss" scoped=true>

p {
	margin-top: 2em;
}

</style>
