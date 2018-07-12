[![Build Status](https://travis-ci.org/JayVora-SerpentCS/OdooEduERP.svg?branch=11.0)](https://travis-ci.org/JayVora-SerpentCS/OdooEduERP)

# EduERPv11
Education ERP v11
Serpent Consulting Services Pvt Ltd, the Official Odoo partner has here contributed the Education ERP.

Help us do better by donating to us and motivating us : http://www.serpentcs.com/page/donate-to-serpentcs
Thanks.

# Guidelines
## License
All modules will be AGPLv3.

## Coding guidelines
All code must follow the [OCA Coding Guidelines](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md).

## Creating a PR in this repository
Please follow the rules of the naming:

### PR Naming Convention

Naming convention: **`[<TAG>][<branch>][T<Task#>] <Description>`**

Where:

    * <TAG> in:
    
        * WIP = Work In Progress
        * IMP = Improvement
        * ADD = New feature
        * MIG = Migration
        * REF = Refactoring
        * FIX= Bug fixing
        * REV = Revert

    * <branch> is the target branch (e.g. same as Odoo version), such as 8.0, 9.0, 10.0, etc.
    * <Task#> is the task ID
    * <Description> is the description of the PR (e.g. name of the TS/project/task)

For instance:

    * [IMP][10.0][TS0010YG][T21336] Report for Sales Invoice and Deliver Packing List for Custom
    * [MIG][master][T20936] Remove hard-code about company information
    * [ADD][11.0][T21525] hr.analytic.timesheet need to reflects the origin of TMS input on Task and Issues
### Issue

Naming convention: **`[<TAG>][<branch>][i<Issue#>] <Description>`**

Where:

    * <Issue#> is the issue ID
    * <Description> is the description of the PR (e.g. name of the issue)
For instance:

    * [FIX][11.0][I4534] The users not from school groups could edit or duplicate users
    * [FIX][master][I4348] Fix in the School search box which you cant search by name of student
    * [FIX][master][I4195] Module error

## Tags
The tags in the repositories and Issues must be maintained with the following meaning:

* For Issues only:

   * 'bug': For bug-related issues. Do not use in PR.
   * 'enhancement': Indicates a new feature when a bug has been qualified as new
     feature or for RFC. Do not use in PR.
   * 'invalid': When an issues is qualified as invalid. Do not use in PR.
   * 'question': for questions-related issues. Do not use in PR.
   * 'wontfix': Bug that will not be fixed for any reason (obsolete, not in
     scope etc.). Do not use in PR.
* For PR only:

   * 'work in progress': whenever a PR is not yet ready for review. Do not use in Issues.
   * 'needs fixing': when the PR needs to be fixed (eg: after reviewer comments).
     Do not use in Issues.
* For both PR and Issues:

   * 'duplicate': To qualify duplicated questions or PR
   * 'help wanted': Whenever the Issue or PR need some additional help
   * 'needs review': When a PR is ready for review.

