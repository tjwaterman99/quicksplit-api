var axios = require('axios');
var Cookies = require('js-cookie');


class Client {
	constructor(baseURL) {
		this.baseURL = baseURL
		this.tokenKey = 'token'
		this.token = Cookies.get(this.tokenKey) || null
		this.user = null
		this.axios = axios.create({
			baseURL: this.baseURL
		})

		if (this.token != null) {
			this.setAuthorizationHeader()
			this.getUser()
		}
	}

	setAuthorizationHeader() {
		this.axios.defaults.headers.Authorization = this.token
		return this.axios.defaults.headers.Authorization
	}

	removeAuthorizationHeader() {
		this.axios.defaults.headers.Authorization = null
		return this.axios.defaults.headers.Authorization
	}

	async login({email, password}) {
		var request = this.axios.post('/login', {
			'email': email,
			'password': password
		})

		var self = this

		return request.then(resp => {
			self.token = resp.data.data.admin_token.value
			self.user = resp.data.data
			Cookies.set(self.tokenKey, self.token)
			self.setAuthorizationHeader()
			return resp
		})
	}

	async register({email, password}) {
		var request = this.axios.post('/user', {
			'email': email,
			'password': password
		})

		var self = this

		return request.then(resp => {
			self.token = resp.data.data.admin_token.value
			self.user = resp.data.data
			Cookies.set(self.tokenKey, self.token)
			self.setAuthorizationHeader()
			return resp
		})
	}

	logout() {
		Cookies.remove(this.tokenKey);
		this.removeAuthorizationHeader()
		this.token = null
		return this.token
	}

	get(route, data) {
		return this.axios.get(route, data)
	}

	post(route, data) {
		return this.axios.post(route, data)
	}

	getUser() {
		if (this.user) {
			return this.user
		}
		this.get('/user')
				.then(resp => {
					this.user = resp.data.data
				}).catch(err => {
					console.log(err)
					this.user = null
				})
		return this.user
	}
}

export default Client
