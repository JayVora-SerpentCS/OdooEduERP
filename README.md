# OCA Addons Repo Template

This is a template created to make easier the task of maintaining OCA addon
repositories.

## Why?

We have dozens of repos. Most of them look the same, and most of them need
specific-but-similar configurations for CI, code quality, dependency management, etc.

We need a place where to evolve those things and push them automatically everywhere
else.

This is that place.

## How to use?

This is a template. It is based on [Copier](https://github.com/pykong/copier), go there
to read its docs to know how it works.

Quick answer to bootstrap a new repo:

```bash
# Install copier and pre-commit if missing
pipx install copier
pipx install pre-commit
pipx ensurepath
# Clone this template and answer its questions
copier copy https://github.com/OCA/oca-addons-repo-template.git some-repo
# Commit that
cd some-repo
git add .
pre-commit install
pre-commit run -a
git commit -am 'Hello world 🖖'
```

Quick answer to update a repo:

```bash
# Update the repo
cd some-repo
copier update
# Reformat updated files
pre-commit run
# Commit update
git commit -am 'Updated from template'
# Reformat all other files, in case some pre-commit configuration was updated
pre-commit run -a || git commit -am 'Reformatted after template update'
```

## How to contribute?

Go read [our contribution guideline](CONTRIBUTING.md).

## Supported use cases

This template allows to bootstrap and update addon repositories for these Odoo versions:

- 13.0

Future versions will be added as they are released. Past versions could be added as long
as they don't break existing branches.

Right now this template is tightly coupled with code, guidelines and decisions from OCA.
You might find some things that you can reuse in your own templates, but in general
terms this template is not meant to support being used as is for other organizations.

## The legal stuff

Copyright holder: [Odoo Community Association](https://odoo-community.org/).

Template license: [MIT](LICENSE)

License of the rendered repositories: [AGPL](LICENSE.jinja)

License of each module in those rendered repositories: Depends on the module.
