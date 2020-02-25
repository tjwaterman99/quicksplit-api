# Roadmap

## Finish the CLI and backend

- [X] Build out a better CLI test suite.
- [X] Do the refactor (routes, etc)
- [X] Capture more data in the experiments (last exposure, etc)

## Scale Heroku
- [X] hobby web
- [X] hobby database (10M rows))

## Configure domains
- [X] api
- [X] www

## Distribute the CLI on PyPI
- [X] CI releases on tags
- [ ] Test releases against the production instance
- [ ] Test previous releases against the production instance [all production releases should include these tests]

## Create a landing page
- [ ]Install instructions
- [ ] Basic styling (just copy Github's styles)

## Youtube Demo video, YT ads, start driving traffic
- [ ] Script written
- [ ] Video recorded (<5 Minutes, launch a real experiment on quicksplit homepage)

## Funnel monitor
- [ ] Basic funnel view in Google sheets for each week (video exposures, conversions, accounts created, etc). We can build out the funnel view in more detail as we get closer.

## Application performance monitor and logging
- [ ] Set up Papertrail
- [ ] Add /events route and logging in the CLI

## Notifications
- [ ] New user signup confirmation
- [ ] New user signup notification to me
- [ ] Password resets

## Review apps, Heroku pipelines, prod & staging instances
- [ ] Don't use docker-based deploys for Heroku, since Heroku doesn't support pipelines for those apps
