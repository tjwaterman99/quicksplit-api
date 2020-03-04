<template>
  <div id="app">
    <div class="container-fluid menu" hidden>
      <div class="row">
        <div class="col-sm-12">
            <span><a href="#faq">FAQ</a></span>
            <span><a href="#contact">Contact</a></span>
            <span><a href="#get-started">Get started</a></span>
        </div>
      </div>
    </div>
    <div class="container-fluid marquee">
      <div class="row">
        <div class="col-sm-12">
          <svg class="logo" version="1.1" viewBox="0.0 0.0 960.0 540.0" fill="none" stroke="none" stroke-linecap="square" stroke-miterlimit="10" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg"><clipPath id="p.0"><path d="m0 0l960.0 0l0 540.0l-960.0 0l0 -540.0z" clip-rule="nonzero"/></clipPath><g clip-path="url(#p.0)"><path fill="#000000" fill-opacity="0.0" d="m0 0l960.0 0l0 540.0l-960.0 0z" fill-rule="evenodd"/><path fill="#ee6c4d" d="m502.10464 163.49783l0 0c63.319427 -13.119553 127.910126 15.873795 160.18906 71.90541c32.27899 56.0316 24.958923 126.451675 -18.154236 174.64638c-43.11316 48.19467 -112.28613 63.283478 -171.55347 37.421173c-59.267334 -25.862274 -95.24872 -86.836914 -89.236206 -151.2211l83.31314 7.780182l0 0c-2.6539001 28.419159 13.2282715 55.333374 39.388885 66.74899c26.160583 11.415619 56.693542 4.755432 75.723694 -16.5177c19.030151 -21.273163 22.26123 -52.356567 8.013306 -77.08893c-14.247986 -24.732346 -42.7583 -37.530014 -70.70746 -31.739044z" fill-rule="evenodd"/><path fill="#ee6c4d" d="m335.0532 80.60887l0 0c62.260406 -38.937515 143.56699 -27.00142 192.00925 28.187645c48.44232 55.189064 49.735596 137.35693 3.0541992 194.04321c-46.681366 56.68631 -127.57202 71.175354 -191.02701 34.216583c-63.454987 -36.9588 -90.762695 -114.46698 -64.4884 -183.0392l73.409454 28.127731c-12.485565 32.585526 0.49105835 69.41742 30.644867 86.980225c30.15384 17.562805 68.59305 10.677612 90.77606 -16.259705c22.182983 -26.937332 21.56842 -65.983505 -1.451355 -92.209335c-23.019775 -26.225845 -61.656677 -31.897888 -91.2428 -13.394775z" fill-rule="evenodd"/></g></svg>
          <h1>Quick Split</h1>
          <h2>The developer tool for fast A/B tests</h2>
        </div>
      </div>
    </div>

    <p class="anchor" id="get-started"></p>
    <div class="container">
    <div class="row">
    <div class="col-12 col-lg-8 offset-lg-2">
    <div class="section">
    <h3>Register an account</h3>
    <hr>
    <p>Download the CLI (requires Python3.7+ and pip installed on your system).</p>
    <pre>
    $ pip install --user quicksplit
    </pre>
    <p>Register a new account.</p>
    <pre>
    $ quicksplit register
    </pre>
    <p>You'll be prompted for an email address and password. (We promise never to send you unhelpful marketing emails).</p>
    <p>Create an experiment.</p>
    <pre>
    $ quicksplit create landing-page-test
    </pre>
    <p>You'll use the name of the experiment in the next steps, where you'll log exposure and conversion events for the experiment.<p>
    <p>But before you can log events, you'll need to locate the <i><b>public, staging</b></i> token for your account.</p>
    <pre>
    $ export TOKEN=$(quicksplit tokens --staging --public)
    </pre>

    <p><b>Public</b> tokens provide for limited access to your account, only allowing logging events. They should always be used in client-side applications such as a JavaScript web app.</p>
    <p><b>Staging</b> tokens are used to separate staging data from production data. They should be used in your development environment.</p>
    <br>
    <h3>Log an exposure event</h3>
    <hr>
    <p>Log an <i>exposure</i> for your experiment by sending JSON encoded data to the <code>/exposures</code> route.</p>
    <pre>
    $ curl https://api.quicksplit.io/exposures \
    -H "Authorization: ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "experiment": "landing-page-test",
      "subject": 12345,
      "cohort": "control"
    }'
    </pre>
    <p>Exposures have three required fields: experiment, subject, and cohort.
    <ul>
    <li><code>experiment</code> is the name of the experiment you created previously. In this case, it's <code>landing-page-test</code></li>
    <li><code>subject</code> is typically a user id provided by your own backend.</li>
    <li><code>cohort</code> corresponds to which version of your application the user is experiencing. In an A/B test, you might use the labels "experimental" and "control" for your cohorts.</li>
    </ul>
    </p>

    <br>
    <h3>Log a conversion event</h3>
    <hr>
    <p>Log a <i>conversion</i> for your experiment by sending JSON encoded data to the <code>/conversions</code> route.</p>
    <pre>
    $ curl https://api.quicksplit.io/conversions \
    -H "Authorization: " \
    -H "Content-Type: application/json" \
    -d '{
      "experiment": "landing-page-test",
      "subject": 12345
    }'
    </pre>


    <p>Confirm that the exposure and conversion logging was successful by checking the recent events.</p>

    <pre>
    $ quicksplit recent --staging

    ┌────────────┬───────────────────┬─────────┬─────────┬───────┬───────────────────────────────┐
    │ Type       │ Experiment        │ Subject │ Cohort  │ Value │ Last seen                     │
    ├────────────┼───────────────────┼─────────┼─────────┼───────┼───────────────────────────────┤
    │ conversion │ landing-page-test │ 12345   │ control │       │ Tue, 25 Feb 2020 21:37:52 GMT │
    │ exposure   │ landing-page-test │ 12345   │ control │       │ Tue, 25 Feb 2020 21:34:35 GMT │
    └────────────┴───────────────────┴─────────┴─────────┴───────┴───────────────────────────────┘
    </pre>

    <p>Note that we used the special <code>--staging</code> flag to retrieve recent staging events. Omitting that flag would pull recent production events instead.</p>

    <br>
    <h3>Download the results of your experiment</h3>
    <hr>

    <p>You can retrieve the statistical significance of your experiment as soon as it has started receiving events.</p>

    <pre>
    $ quicksplit results landing-page-test --staging

    ┌─────────┬──────────┬─────────────────┬────────────────────┐
    │ Cohort  │ Subjects │ Conversion rate │ 95% conf. interval │
    ├─────────┼──────────┼─────────────────┼────────────────────┤
    │ control │ 1        │ 1               │ [,]                │
    └─────────┴──────────┴─────────────────┴────────────────────┘
    Your test is not statistically significant. Either you need to collect more data, or there is no difference in means between the cohorts
    </pre>

    <p>Note that we're using the <code>--staging</code> flag here again because we've been using the staging token.</p>

    </div>
    </div>
    </div>

    <p class="anchor" id="faq"></p>
    <div class="row">
    <div class="col-12 col-lg-8 offset-lg-2">
    <div class="section faq">
    <h2 class="text-center">Frequently asked questions</h2>
    <br>
    <p class="faq-question"><b>Q: What sample sizes can I use for a single experiment?</b></p>
    <p>You can log up to <b>3,000 subjects</b> in a single experiment. In typical situations, that's a large enough sample size to detect ~1% differences in conversion rates.<p>
    <hr>
    <p class="faq-question"><b>Q: Can I run multiple experiments at the same time?</b></p>
    <p>You can run up to <b>three concurrent experiments</b> on a single account. To stop an existing experiment, use the command <code>quicksplit stop</code>. To restart an experiment, use the command <code>quicksplit start</code>.<p>
    <hr>
    <p class="faq-question"><b>Q: Can I do a three-way test (an A/B/C test)?</b></p>
    <p>You can use any number of cohorts for your experiment, including running three way tests.<p>
    <hr>
    <p class="faq-question"><b>Q: How do you calculate whether my experiment is statistically significant?</b></p>
    <p>We use the industry-standard methodology called an <b><a href="https://en.wikipedia.org/wiki/Analysis_of_variance">ANOVA</a></b> test. If the F-statistic of the ANOVA test has an associated p-value of less than 0.1, we conclude that the test is significant.<p>
    <hr>
    </div>
    </div>
    </div>

  <Contact />
  </div>
</div>
</template>

<script>
import Contact from './components/Contact'

export default {
  name: 'App',
  components: {
    'Contact': Contact
  }
}
</script>

<style>

</style>
