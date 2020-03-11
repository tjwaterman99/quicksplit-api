<template>
		<div class="dashboard">
			<div v-if="loaded">
				<div v-if="experiments.length > 0">
					<ul class="list-group" v-for="experiment in experiments" :key="experiment.id">
						<li class="list-group-item">
							{{ experiment.name }} (active={{ experiment.active }})
							<div class="progress">
								<div class="progress-bar" v-bind:style="experimentStyle(experiment)" role="progressbar"></div>
							</div>
						</li>
					</ul>
				</div>
				<div class="text-center">
					<button class="btn btn-secondary btn-lg" data-toggle="modal" data-target="#exampleModal">Create experiment</button>
				</div>
			</div>
			<div v-else class="text-center">
				<div class="spinner-border" role="status">
				</div>
			</div>

			<div class="modal fade" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
				<div class="modal-dialog" role="document">
				<div class="modal-content">
				<div class="modal-header">
				<h5 class="modal-title" id="exampleModalLabel">Start a new experiment</h5>
				<button type="button" class="close" data-dismiss="modal" aria-label="Close">
				<span aria-hidden="true">&times;</span>
				</button>
				</div>
				<div class="modal-body">
					<form>
						<div class="form-group">
							<label for="experimentName">Experiment Name</label>
							<input class="form-control" id="experimentName" v-model="experimentName"/>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
					<button type="button" class="btn btn-primary" @click="createExperiment">Create experiment</button>
				</div>
				</div>
				</div>
				</div>
			</div>
</template>

<script>
var $ = require('jquery');


export default {
	name: "Dashboard",
	data: function() {
		return {
			experiments: [],
			loaded: false,
			experimentName: null
		}
	},
	created: function() {
		var that = this;
		this.$api.get('/experiments').then(function(resp) {
			that.experiments = resp.data.data
			that.loaded = true
		}).catch(function(err) {
			console.log(err)
		})
	},
	methods: {
		createExperiment: function(event) {
			event.preventDefault()
			var that = this;
			this.$api.post('/experiments', {
				name: this.experimentName
			}).then(function(resp) {
				// We should reload the experiments here to get the last "active" updates
				that.experiments.push(resp.data.data)
				var modal = $('#exampleModal')
				modal.modal('hide')
			}).catch(function(err) {
				console.log(err)
			})
		},
		experimentStyle: function(experiment) {
			var width = experiment.subjects_counter / this.$api.user.account.plan.max_subjects_per_experiment + "%"
			return {
				width: width
			}
		}
	}
}
</script>

<style lang='scss' scoped=true>
.dashboard {
	padding: 0em;
}
</style>
