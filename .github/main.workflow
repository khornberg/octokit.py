workflow "Publish to PyPi" {
  on = "push"
  resolves = [
    "PyPi Twine Upload",
  ]
}

action "action-filter" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Package" {
  uses = "khornberg/python-actions/setup-py/3.7@master"
  args = "bdist_wheel sdist"
  needs = ["action-filter"]
}

action "PyPi Twine Upload" {
  uses = "khornberg/python-actions/twine@master"
  needs = ["Package"]
  args = "upload dist/*"
  secrets = ["TWINE_USERNAME", "TWINE_PASSWORD"]
}
