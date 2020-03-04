<template>
  <div id="app">
    <NavBar />
    <Marquee />
    <GetStarted />
    <FaqList />
    <Contact />
</div>
</template>

<script>
import Contact from './components/Contact'
import FaqList from './components/faq/FaqList'
import GetStarted from './components/guides/GetStarted'
import NavBar from './components/NavBar'
import Marquee from './components/Marquee'

export default {
  name: 'App',
  components: {
    'Contact': Contact,
    'FaqList': FaqList,
    'GetStarted': GetStarted,
    'NavBar': NavBar,
    'Marquee': Marquee
  }
}
</script>

<style>

</style>
