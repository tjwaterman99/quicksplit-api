<template>
	<div>
		<Header>Add credit card</Header>
	<div class="container">
		<div class="row">
			<div class="col-lg-6 offset-lg-3">
			<form class="payment-method">
				<div class="form-group">
					<div id="card-number" ></div>
				</div>
				<div class="form-row">
					<div class="col">
						<div id="card-cvc"></div>
					</div>
					<div class="col">
						<div id="card-expiry"></div>
					</div>
				</div>
				<div class="form-group">
					<button type="submit" class="btn btn-primary btn-block submit" @click="handleAddPayment">Add credit card</button>
				</div>
			</form>
			</div>
		</div>
	</div>
	</div>
</template>


<!--
note the other types of Stripe elements besides just card are documented here:
https://stripe.com/docs/js/elements_object/create_element?type=cardNumber

TODO: have the card element send data to Stripe, and trigger a webook to our
server which stores the payment method token. We can test the payments on
localhost using the stripe CLI: https://stripe.com/docs/webhooks/test
-->
<script src="https://js.stripe.com/v3/"></script>
<script>
import Header from '../Header';

var stripe = new Stripe('pk_test_vs6w4emCv9szUa8mJyeXKTey00IV5800C2');
var elements = stripe.elements()
var cardExpiryElement = elements.create('cardExpiry');
var cardCvcElement = elements.create('cardCvc');
var cardNumberElement = elements.create('cardNumber');

export default {
	name: "Payments",
	components: {
		"Header":  Header
	},
	data: function() {
		return {
			cardNumberComplete: false,
			cardExpiryComplete: false,
			cardCvcComplete: false,
		}
	},
	methods: {
		handleAddPayment: function(event) {
			event.preventDefault()
			var that = this;
			stripe.createPaymentMethod({
				type: 'card',
				card: cardNumberElement,
				billing_details: {
					email: that.$api.user.email
				}
			})
		}
	},
	mounted: function() {
		var that = this;

		cardNumberElement.on('change', function(event) {
			that.cardNumberComplete = event.complete
		});

		cardExpiryElement.on('change', function(event) {
			that.cardExpiryComplete = event.complete
		})

		cardCvcElement.on('change', function(event) {
			that.cardCvcComplete = event.complete
		})

		cardNumberElement.mount("#card-number");
		cardExpiryElement.mount("#card-expiry");
		cardCvcElement.mount("#card-cvc");
	}
}
</script>

<style lang="scss" scoped=true>
.payment-method {
	padding-top: 3em;
}

.StripeElement {
	border: 1px solid black;
	padding: 0.5em;
	font-size: 1em !important;
	border-radius: 0.5em;
}

.submit {
	margin-top: 1em;
}
</style>
