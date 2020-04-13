import pytest
from octokit import errors
from octokit.base import Base


class TestBase(object):
    def test_validate_required_parameters(self):
        attrs = {"owner": "me", "repo": "my_repo"}
        assert Base().validate(attrs, self.parameter_only_definition)

    def test_raise_error_for_missing_required_parameter(self):
        attrs = {"owner": "me"}
        with pytest.raises(errors.OctokitParameterError) as e:
            Base().validate(attrs, self.definition)
        assert "repo is a required parameter" == str(e.value)

    def test_raise_error_for_missing_required_request_body_property(self):
        attrs = {"owner": "me", "repo": "my_repo"}
        with pytest.raises(errors.OctokitParameterError) as e:
            Base().validate(attrs, self.definition)
        assert "name is a required parameter" == str(e.value)
        attrs = {"owner": "me", "repo": "my_repo", "name": "blah"}
        with pytest.raises(errors.OctokitParameterError) as e:
            Base().validate(attrs, self.definition)
        assert "head_sha is a required parameter" == str(e.value)

    def test_validate_parameters_and_request_body_properties(self):
        attrs = {"owner": "me", "repo": "my_repo", "name": "blah", "head_sha": "master"}
        assert Base().validate(attrs, self.definition)

    def test_validate_nested_request_body_properties(self):
        attrs = {"owner": "me", "repo": "my_repo", "name": "blah", "head_sha": "master", "output": {}}
        with pytest.raises(errors.OctokitParameterError) as e:
            Base().validate(attrs, self.definition)
        assert "title is a required parameter" == str(e.value)
        attrs = {"owner": "me", "repo": "my_repo", "name": "blah", "head_sha": "master", "output": {"title": "here"}}
        with pytest.raises(errors.OctokitParameterError) as e:
            Base().validate(attrs, self.definition)
        assert "summary is a required parameter" == str(e.value)
        attrs = {
            "owner": "me",
            "repo": "my_repo",
            "name": "blah",
            "head_sha": "master",
            "output": {"title": "here", "summary": "there"},
        }
        assert Base().validate(attrs, self.definition)

    @property
    def definition(self):
        return {
            "parameters": [
                {
                    "name": "accept",
                    "description": "This API is under preview and subject to change.",
                    "in": "header",
                    "schema": {"type": "string", "default": "application/vnd.github.antiope-preview+json"},
                    "required": True,
                },
                {
                    "name": "owner",
                    "description": "owner parameter",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
                {
                    "name": "repo",
                    "description": "repo parameter",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
            ],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": 'The name of the check. For example, "code-coverage".',
                                },
                                "head_sha": {"type": "string", "description": "The SHA of the commit."},
                                "details_url": {"type": "string"},
                                "external_id": {
                                    "type": "string",
                                    "description": "A reference for the run on the integrator's system.",
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["queued", "in_progress", "completed"],
                                    "default": "queued",
                                },
                                "started_at": {"type": "string"},
                                "conclusion": {
                                    "type": "string",
                                    "enum": [
                                        "success",
                                        "failure",
                                        "neutral",
                                        "cancelled",
                                        "timed_out",
                                        "action_required",
                                    ],
                                },
                                "completed_at": {"type": "string"},
                                "output": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string", "description": "The title of the check run."},
                                        "summary": {"type": "string"},
                                        "text": {"type": "string"},
                                        "annotations": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "path": {"type": "string"},
                                                    "start_line": {
                                                        "type": "integer",
                                                        "description": "The start line of the annotation.",
                                                    },
                                                    "end_line": {
                                                        "type": "integer",
                                                        "description": "The end line of the annotation.",
                                                    },
                                                    "start_column": {"type": "integer"},
                                                    "end_column": {"type": "integer"},
                                                    "annotation_level": {
                                                        "type": "string",
                                                        "enum": ["notice", "warning", "failure"],
                                                    },
                                                    "message": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "raw_details": {"type": "string"},
                                                },
                                                "required": [
                                                    "path",
                                                    "start_line",
                                                    "end_line",
                                                    "annotation_level",
                                                    "message",
                                                ],
                                            },
                                        },
                                        "images": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "alt": {
                                                        "type": "string",
                                                        "description": "The alternative text for the image.",
                                                    },
                                                    "image_url": {
                                                        "type": "string",
                                                        "description": "The full URL of the image.",
                                                    },
                                                    "caption": {
                                                        "type": "string",
                                                        "description": "A short image description.",
                                                    },
                                                },
                                                "required": ["alt", "image_url"],
                                            },
                                        },
                                    },
                                    "required": ["title", "summary"],
                                },
                                "actions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "label": {"type": "string"},
                                            "description": {"type": "string"},
                                            "identifier": {"type": "string"},
                                        },
                                        "required": ["label", "description", "identifier"],
                                    },
                                },
                            },
                            "required": ["name", "head_sha"],
                        }
                    }
                }
            },
        }

    @property
    def parameter_only_definition(self):
        return {
            "parameters": [
                {
                    "name": "accept",
                    "description": "This API is under preview and subject to change.",
                    "in": "header",
                    "schema": {"type": "string", "default": "application/vnd.github.antiope-preview+json"},
                    "required": True,
                },
                {
                    "name": "owner",
                    "description": "owner parameter",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
                {
                    "name": "repo",
                    "description": "repo parameter",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
            ]
        }
