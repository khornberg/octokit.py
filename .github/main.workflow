workflow "Publish to PyPi" {
  resolves = [
    "PyPi Twine Upload",
  ]
  on = "push"
}

action "Master Branch Filter" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Merged" {
  uses = "actions/bin/filter@master"
  args = "merged true"
  needs = ["Master Branch Filter"]
}

action "Package" {
  uses = "khornberg/python-actions/setup-py/3.7@master"
  args = "bdist_wheel sdist"
  needs = ["Merged"]
}

action "PyPi Twine Upload" {
  uses = "khornberg/python-actions/twine@master"
  needs = ["Package"]
  args = "upload dist/*"
  secrets = ["TWINE_USERNAME", "TWINE_PASSWORD"]
}

# PR workflow

workflow "Test" {
  resolves = [
    "Report",
    "Lint",
    "Docs",
  ]
  on = "pull_request"

  # PR workflow

  # PR workflow
}

action "Branch Filter" {
  uses = "actions/bin/filter@master"
  args = "not branch master"
}

action "Filter" {
  uses = "actions/bin/filter@master"
  args = "action 'opened|synchronize'"
  needs = ["Branch Filter"]
}

action "Curl" {
  uses = "actions/bin/curl@master"
  args = "curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter"
  needs = ["Filter"]
}

action "Prepare" {
  uses = "actions/bin/sh@master"
  args = ["chmod +x ./cc-test-reporter && ./cc-test-reporter before-build"]
  secrets = ["CC_TEST_REPORTER_ID"]
  needs = ["Curl"]
}

action "Requirements 3.6" {
  uses = "jefftriplett/python-actions@master"
  args = "pip install tox"
  needs = ["Prepare"]
}

action "Test 3.6" {
  uses = "jefftriplett/python-actions@master"
  args = "tox -e py36 -v"
  needs = ["Requirements 3.6"]
}

action "Lint" {
  uses = "jefftriplett/python-actions@master"
  args = "tox -e check -v"
  needs = ["Requirements 3.6"]
}

action "Docs" {
  uses = "jefftriplett/python-actions@master"
  args = "tox -e docs -v"
  needs = ["Requirements 3.6"]
}

action "Report" {
  uses = "actions/bin/sh@master"
  args = ["apt-get update && apt-get install git-core -y && ./cc-test-reporter after-build --coverage-input-type coverage.py"]
  needs = ["Test 3.6"]
  secrets = ["CC_TEST_REPORTER_ID"]
}
