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
import Client from './client';

const routes = [
  { path: '/faq', component: Faq },
  { path: '/',  component: Home },
  { path: '/get-started', component: GetStarted },
  { path: '/contact', component: Contact },
  { path: '/login', component: Login},

  { path: '/*', component: Error404 },
]

const router = new VueRouter({
  routes: routes,
  mode: 'history'
})

Vue.use(VueRouter)
Vue.config.productionTip = false
var api = new Client(process.env.VUE_APP_API_URL)
Vue.observable(api)
Vue.prototype.$api = api

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
