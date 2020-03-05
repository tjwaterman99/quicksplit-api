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


Vue.use(VueRouter)
Vue.config.productionTip = false

const routes = [
  { path: '/faq', component: Faq },
  { path: '/',  component: Home },
  { path: '/get-started', component: GetStarted },
  { path: '/contact', component: Contact },

  { path: '/*', component: Error404 },
]

const router = new VueRouter({
  routes: routes,
  mode: 'history'
})

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
