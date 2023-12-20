# Git and GitHub

In this guide, we'll discuss our best practices when interacting with Git and GitHub.

All source code is managed in GitHub repositories in the
[populationgenomics organization](https://github.com/populationgenomics). Please
let your manager know if you're not a member of either the
[software or analysis team](https://github.com/orgs/populationgenomics/teams)
yet.

## New repositories

> See [New repository](/new_repository.md) for more information

If you need a new repository, please reach out to the software team. As a principle, we try to use public repositories with an MIT license whenever possible. Unless the repo is forked, only enable the "squash merge" button, and enable branch protection rules.

## Git setup

Please add your `@populationgenomics.org.au` email address in your GitHub
account settings and use this address when setting up your `git` user config, though you could also consider using the noreply email address found in your GitHub profile.

It's also a good idea to send any notifications for the populationgenomics
organization to your work email address using GitHub's [Custom Routing](https://github.com/settings/notifications/custom_routing) feature..
settings under Notifications.

### Connection protocol

Checking out a repo using both SSH and HTTPS are fine. SSH mayb be more secure as it's usually possible to extract the GitHub password from the credential manager (eg: keychain on MacOS), but some institites internet may block SSH.

If using SSH, we recommend generating a key with the ed25519 algorithm. This guide from Github gives a good overview of [generating and uploading SSH keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).

If using HTTPS, we recommend using the [Github CLI](https://docs.github.com/en/get-started/getting-started-with-git/caching-your-github-credentials-in-git#github-cli).

### Signing commits

Signing commits gives us extra confidence that commits are signed by you. Traditionally you'd sign a commit with a GPG key, but it's possible to sign commits with an SSH key. [this guide](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key#telling-git-about-your-ssh-key) gives good instructions on how to set up a signing key with Git - but the highlights:

```shell
git config --global gpg.format ssh
git config --global user.signingkey /PATH/TO/.SSH/KEY.PUB

# To sign all commits by default, you can run:
git config --global commit.gpgsign true
```

## Working and pull-requests

> Note: We expect this guide to change in early to mid 2024

We _strongly_ encourage you to create a draft pull-request as soon as reasonable. It creates a good public record of your work that's easy to follow along and engage with.

Don't be too concerned with the initial naming of a draft pull request, give enough context, add some description - you can update these fields later.

As we squash merge commits, we aren't too concerned with in-progress commit messages - hence pull request title carries this importance. We currently do NOT have clear guidelines on PR naming and formatting.

### Code reviews

There are many advantages of having code reviews:

- Catch bugs and bad design decisions earlier.
- Improve the overall readability and maintainability of the code.
- Spread knowledge about the code base within the team.
- Learn from others by reading their code.

If you're not used to code reviews, don't be intimidated. After a short period of time, they'll feel very natural. It's one of the best ways to truly work together on a shared code base.

For code reviews to work well, it's helpful to follow a few general guidelines. Please take a look at this [excellent article](https://mtlynch.io/code-review-love/) about good code review practices and consider the following suggestions:

- Don't interpret review comments as criticism of your code. Instead, consider them an opportunity to improve the code and learn new techniques.
- It's really important that reviews are done in a timely fashion. Try to respond to review requests within 24 hours. Use GitHub's [scheduled reminders](https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/managing-your-scheduled-reminders) to receive notifications in Slack when reviews need your attention. You can [set up real-time alerts](https://github.com/settings/reminders/populationgenomics) to get Slack notifications when you're mentioned in an issue or comment.
- If you've addressed all review comments, click the "Re-request review" button to let the reviewer know it's their turn. If you don't hear back from a reviewer, feel free to "ping" them on Slack.
- In order for people to respond quickly to reviews, individual pull requests (PRs) need to be small. Don't send thousands of lines of code for review: that's not fun for the reviewer, and it's unlikely you'll get good review feedback. Instead, send small PRs frequently, so the reviewer can really focus on the change.
- If a reviewer doesn't understand the code or has a question about it, it's likely that a future maintainer will have a similar problem. Therefore, don't just respond to the question using the review comment UI, but think about how to make the code more readable. Should there be a clarifying code comment, could you change the structure of the code, or rename a function or variable to avoid the confusion?
- Code reviews are very different from pair programming. It's an asynchronous activity. Make sure to prepare your PR in a way that preempts any questions you can anticipate, to speed up the overall process.
- It's normal that there might be a few rounds of back-and-forth. However, a review should always be a technically focussed conversation, with the common goal to improve the quality of the code. As a reviewer, make concrete suggestions on how to improve the code.

It's okay to spend a lot of time on reviews! This is a big part of your responsibilities, and we really care about high code quality.

To review someone else’s PR, click on "Files changed". This will show the diff between the old code and the new proposed changes. You can make comments on specific lines of the code. Feel free to ask questions here, especially if you don’t understand something! It’s a good idea to think critically about the changes. There should also be tests either added or existing to make sure the code changes do not break any existing functionality and actually implement what was intended.

If there are items for the author to address, then submit your review with "Request Changes". Otherwise, once you are happy with the changes and all comments have been addressed, you can "Approve" the PR.

After approving, you can also merge the PR. Unless you added any feedback (even minor one: thoughts, minor suggestions, pointers to something related) - in this case, it's preferrable to leave merging to the author in case the author wants to act on your feedback.

Before merging, double-check that all review comments have been addressed. Preferably use "squash merging" to keep the history clean; the exception to this are upstream merges where you want to keep the complete commit history.

If you are the person whose code is being reviewed, and your PR is in the "Request Changes" state, then you’ll need to address their comments by pushing new commit changes or answering questions. Once you are done, then you can dismiss their review towards the bottom of the Conversation page.

We set up repositories in a way that requires at least one code review before you can merge a pull request into the `main` branch. You can freely commit to any development branches.


### PR naming proposal

This is one suggestion, but we plan to formalise this in early to mid 2024:

> PR titles could follow the format:
>
>     <TYPE>[<scope>]: <MESSAGE>`
>
> The type is one of the following:
>
> - `fix`: for patching a bug in the codebase
> - `feat`: new feature to the codebase
> - `chore`: changes that complete routine / automated tasks (eg: upgrading deps)
> - `docs`: Documentation only / non-functional update
> - `revert`: A change that reverts a previous change
>
> The scope could be:
>
> - `!`: for a breaking change
>
> Example:
> > `feat!`: new endpoint added to achieve functionality
