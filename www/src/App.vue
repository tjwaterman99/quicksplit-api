<template>
  <div id="app">
    <div v-if="dashboard" class="dashboard">
      <div>
        <div class="row">
        <div class="col-md-2">
          <DashboardNavBar />
        </div>
        <div class="col-md-10">
          <router-view />
        </div>
      </div>
      </div>
    </div>
    <div v-else class="public">
      <NavBar />
      <router-view />
    </div>
</div>
</template>

<script>
import NavBar from './components/NavBar'
import DashboardNavBar from './components/DashboardNavBar'

export default {
  name: 'App',
  components: {
    'NavBar': NavBar,
    'DashboardNavBar': DashboardNavBar
  },
  computed: {
    dashboard: function() {
      return this.$route.path.match('/dashboard')
    }
  }
}
</script>

<style>

#app {
  min-height: 100%;
  height: 100%;
}

.dashboard {
  background-color: #E4E8EE;
  min-height: 100%;
  padding: 1em;
}

</style>
