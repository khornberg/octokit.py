workflow "Publish to PyPi" {
  on = "push"
  resolves = [
    "PyPi Twine Upload",
  ]
}

action "Master Workflow" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Package" {
  uses = "khornberg/python-actions/setup-py/3.7@master"
  args = "bdist_wheel sdist"
  needs = ["Master Workflow"]
}

action "PyPi Twine Upload" {
  uses = "khornberg/python-actions/twine@master"
  needs = ["Package"]
  args = "upload dist/*"
  secrets = ["TWINE_USERNAME", "TWINE_PASSWORD"]
}

# PR workflow

workflow "Test" {
  on = "push"
  resolves = [
    "Report", "Lint", "Docs"
  ]
}

action "Filter" {
  uses = "actions/bin/filter@master"
  args = "not branch master"
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

