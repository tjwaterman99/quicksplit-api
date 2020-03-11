import './assets/scss/styles.scss';
import 'bootstrap';

import Vue from 'vue';
import VueRouter from 'vue-router';
import App from './App.vue';
import Faq from './components/pages/Faq';
import Home from './components/pages/Home';
import GetStarted from './components/pages/GetStarted';
import Contact from './components/pages/Contact';
import Error404 from './components/pages/Error404';
import Login from './components/pages/Login';
import Dashboard from './components/pages/Dashboard';
import Payments from './components/pages/Payments';
import Tokens from './components/dashboard/views/Tokens';
import Account from './components/dashboard/views/Account';

import Client from './client';

const routes = [
  { path: '/faq', component: Faq },
  { path: '/',  component: Home },
  { path: '/get-started', component: GetStarted },
  { path: '/contact', component: Contact },
  { path: '/login', component: Login },
  { path: '/payments', component: Payments },
  { path: '/dashboard', component: Dashboard},
  { path: '/dashboard/tokens', component: Tokens},
  { path: '/dashboard/account', component: Account },

  { path: '/*', component: Error404 },
]

const router = new VueRouter({
  routes: routes,
  mode: 'history'
})

Vue.use(VueRouter)
Vue.config.productionTip = false

var api = new Client(process.env.VUE_APP_API_URL)
var stripe_public_key = process.env.VUE_APP_STRIPE_PUBLIC_KEY

Vue.observable(api)

Vue.prototype.$api = api
Vue.prototype.$stripe_public_key = stripe_public_key

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
