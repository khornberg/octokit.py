workflow "Test" {
  on = "push"
  resolves = [
    "Report", "Lint", "Test 3.7""
  ]
}

action "action-filter" {
  uses = "actions/bin/filter@master"
  args = "not branch master"
}

action "Curl" {
  uses = "actions/bin/curl@master"
  args = "curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter"
  needs = "action-filter"
}

action "Prepare" {
  uses = "actions/bin/sh@master"
  args = ["chmod +x ./cc-test-reporter && ./cc-test-reporter before-build"]
  secrets = ["CC_TEST_REPORTER_ID"]
  needs = ["Curl"]
}

action "Requirements 3.6" {
  uses = "jefftriplett/python-actions@master"
  args = "pip install -r requirements.txt && pip install -r test-requirements.txt"
  needs = ["Prepare"]
}

action "Test 3.6" {
  uses = "jefftriplett/python-actions@master"
  args = "python -m pytest --cov=elasticpypi --cov-report=term-missing --cov-report=xml"
  needs = ["Requirements 3.6"]
}

action "Lint" {
  uses = "jefftriplett/python-actions@master"
  args = "flake8 --max-complexity=6 --max-line-length=120 --exclude node_modules,.requirements,venv"
  needs = ["Requirements 3.6"]
}

action "Requirements 3.7" {
  uses = "khornberg/python-actions/setup-py/3.7@master"
  args = "pip install -r requirements.txt && pip install -r test-requirements.txt"
  needs = ["Prepare"]
}

action "Test 3.7" {
  uses = "khornberg/python-actions/setup-py/3.7@master"
  args = "python -m pytest --cov=elasticpypi --cov-report=term-missing"
  needs = ["Requirements 3.7"]
}

action "Report" {
  uses = "actions/bin/sh@master"
  args = ["apt-get update && apt-get install git-core -y && ./cc-test-reporter after-build --coverage-input-type coverage.py"]
  needs = ["Test 3.6"]
  secrets = ["CC_TEST_REPORTER_ID"]
}
