---
title: Insiders
---

# Insiders

*mkdocstrings* follows the **sponsorware** release strategy, which means that new features are first exclusively released to sponsors as part of [Insiders][]. Read on to learn [what sponsorships achieve][sponsorship], [how to become a sponsor][sponsors] to get access to Insiders, and [what's in it for you][features]!

## What is Insiders?

*mkdocstrings Insiders* is a private fork of *mkdocstrings*, hosted as a private GitHub repository. Almost[^1] [all new features][features] are developed as part of this fork, which means that they are immediately available to all eligible sponsors, as they are granted access to this private repository.

[^1]: In general, every new feature is first exclusively released to sponsors, but sometimes upstream dependencies enhance existing features that must be supported by *mkdocstrings*.

Every feature is tied to a [funding goal][funding] in monthly subscriptions. When a funding goal is hit, the features that are tied to it are merged back into *mkdocstrings* and released for general availability, making them available to all users. Bugfixes are always released in tandem.

Sponsorships start as low as [**$10 a month**][sponsors].[^2]

[^2]: Note that $10 a month is the minimum amount to become eligible for Insiders. While GitHub Sponsors also allows to sponsor lower amounts or one-time amounts, those can't be granted access to Insiders due to technical reasons. Such contributions are still very much welcome as they help ensuring the project's sustainability.

## What sponsorships achieve

Sponsorships make this project sustainable, as they buy the maintainers of this project time – a very scarce resource – which is spent on the development of new features, bug fixing, stability improvement, issue triage and general support. The biggest bottleneck in Open Source is time.[^3]

[^3]: Making an Open Source project sustainable is exceptionally hard: maintainers burn out, projects are abandoned. That's not great and very unpredictable. The sponsorware model ensures that if you decide to use *mkdocstrings*, you can be sure that bugs are fixed quickly and new features are added regularly.

If you're unsure if you should sponsor this project, check out the list of [completed funding goals][goals completed] to learn whether you're already using features that were developed with the help of sponsorships. You're most likely using at least a handful of them, [thanks to our awesome sponsors][sponsors]!

## What's in it for me?

```python exec="1" session="insiders"
data_source = [
    "docs/insiders/goals.yml",
    ("griffe-pydantic", "https://mkdocstrings.github.io/griffe-pydantic/", "insiders/goals.yml"),
    ("griffe-typedoc", "https://mkdocstrings.github.io/griffe-typedoc/", "insiders/goals.yml"),
    ("griffe-warnings-deprecated", "https://mkdocstrings.github.io/griffe-warnings-deprecated/", "insiders/goals.yml"),
    ("mkdocstrings-c", "https://mkdocstrings.github.io/c/", "insiders/goals.yml"),
    ("mkdocstrings-python", "https://mkdocstrings.github.io/python/", "insiders/goals.yml"),
    ("mkdocstrings-shell", "https://mkdocstrings.github.io/shell/", "insiders/goals.yml"),
    ("mkdocstrings-typescript", "https://mkdocstrings.github.io/typescript/", "insiders/goals.yml"),
]
```

<!-- blacken-docs:off -->
```python exec="1" session="insiders" idprefix=""
--8<-- "scripts/insiders.py"

if unreleased_features:
    print(
        "The moment you [become a sponsor](#how-to-become-a-sponsor), you'll get **immediate "
        f"access to {len(unreleased_features)} additional features** that you can start using right away, and "
        "which are currently exclusively available to sponsors:\n"
    )

    for feature in unreleased_features:
        feature.render(badge=True)

    print(
        "\n\nThese are just the features related to this project. "
        "[See the complete feature list on the author's main Insiders page](https://pawamoy.github.io/insiders/#whats-in-it-for-me)."
    )
else:
    print(
        "The moment you [become a sponsor](#how-to-become-a-sponsor), you'll get immediate "
        "access to all released features that you can start using right away, and "
        "which are exclusively available to sponsors. At this moment, there are no "
        "Insiders features for this project, but checkout the [next funding goals](#goals) "
        "to see what's coming, as well as **[the feature list for all Insiders projects](https://pawamoy.github.io/insiders/#whats-in-it-for-me).**"
    )
```
<!-- blacken-docs:on -->

Additionally, your sponsorship will give more weight to your upvotes on issues, helping us prioritize work items in our backlog. For more information on how we prioritize work, see this page: [Backlog management][backlog].

## How to become a sponsor

Thanks for your interest in sponsoring! In order to become an eligible sponsor with your GitHub account, visit [pawamoy's sponsor profile][github sponsor profile], and complete a sponsorship of **$10 a month or more**. You can use your individual or organization GitHub account for sponsoring.

Sponsorships lower than $10 a month are also very much appreciated, and useful. They won't grant you access to Insiders, but they will be counted towards reaching sponsorship goals. Every sponsorship helps us implementing new features and releasing them to the public.

**Important:** By default, when you're sponsoring **[@pawamoy][github sponsor profile]** through a GitHub organization, all the publicly visible members of the organization will be invited to join our private repositories. If you wish to only grant access to a subset of users, please send a short email to insiders@pawamoy.fr with the name of your organization and the GitHub accounts of the users that should be granted access.

**Tip:** to ensure that access is not tied to a particular individual GitHub account, you can create a bot account (i.e. a GitHub account that is not tied to a specific individual), and use this account for the sponsoring. After being granted access to our private repositories, the bot account can create private forks of our private repositories into your own organization, which all members of your organization will have access to.

You can cancel your sponsorship anytime.[^5]

[^5]: If you cancel your sponsorship, GitHub schedules a cancellation request which will become effective at the end of the billing cycle. This means that even though you cancel your sponsorship, you will keep your access to Insiders as long as your cancellation isn't effective. All charges are processed by GitHub through Stripe. As we don't receive any information regarding your payment, and GitHub doesn't offer refunds, sponsorships are non-refundable.


[:octicons-heart-fill-24:{ .pulse } &nbsp; Join our <span id="sponsors-count"></span> awesome sponsors][github sponsor profile]{ .md-button .md-button--primary }

<hr>
<div class="premium-sponsors">
  <div id="gold-sponsors"></div>
  <div id="silver-sponsors"></div>
  <div id="bronze-sponsors"></div>
</div>
<hr>

<div id="sponsors"></div>

<small>
  If you sponsor publicly, you're automatically added here with a link to your profile and avatar to show your support for *mkdocstrings*. Alternatively, if you wish to keep your sponsorship private, you'll be a silent +1. You can select visibility during checkout and change it afterwards.
</small>

## Funding <span class="sponsors-total"></span>

### Goals

The following section lists all funding goals. Each goal contains a list of features prefixed with a checkmark symbol, denoting whether a feature is :octicons-check-circle-fill-24:{ style="color: #00e676" } already available or :octicons-check-circle-fill-24:{ style="color: var(--md-default-fg-color--lightest)" } planned, but not yet implemented. When the funding goal is hit, the features are released for general availability.

```python exec="1" session="insiders" idprefix=""
for goal in goals.values():
    if not goal.complete:
        goal.render()
```

### Goals completed

This section lists all funding goals that were previously completed, which means that those features were part of Insiders, but are now generally available and can be used by all users.

```python exec="1" session="insiders" idprefix=""
for goal in goals.values():
    if goal.complete:
        goal.render()
```

## Frequently asked questions

### Compatibility

> We're building an open source project and want to allow outside collaborators to use *mkdocstrings* locally without having access to Insiders. Is this still possible?

Yes. Insiders is compatible with *mkdocstrings*. Almost all new features and configuration options are either backward-compatible or implemented behind feature flags. Most Insiders features enhance the overall experience, though while these features add value for the users of your project, they shouldn't be necessary for previewing when making changes to content.

### Payment

> We don't want to pay for sponsorship every month. Are there any other options?

Yes. You can sponsor on a yearly basis by [switching your GitHub account to a yearly billing cycle][billing cycle]. If for some reason you cannot do that, you could also create a dedicated GitHub account with a yearly billing cycle, which you only use for sponsoring (some sponsors already do that).

If you have any problems or further questions, please reach out to insiders@pawamoy.fr.

### Terms

> Are we allowed to use Insiders under the same terms and conditions as *mkdocstrings*?

Yes. Whether you're an individual or a company, you may use *mkdocstrings Insiders* precisely under the same terms as *mkdocstrings*, which are given by the [ISC license][license]. However, we kindly ask you to respect our **fair use policy**:

- Please **don't distribute the source code** of Insiders. You may freely use it for public, private or commercial projects, privately fork or mirror it, but please don't make the source code public, as it would counteract the sponsorware strategy.
- If you cancel your subscription, your access to the private repository is revoked, and you will miss out on all future updates of Insiders. However, you may **use the latest version** that's available to you **as long as you like**. Just remember that [GitHub deletes private forks][private forks].

[backlog]: https://pawamoy.github.io/backlog/
[insiders]: #what-is-insiders
[sponsorship]: #what-sponsorships-achieve
[sponsors]: #how-to-become-a-sponsor
[features]: #whats-in-it-for-me
[funding]: #funding
[goals completed]: #goals-completed
[github sponsor profile]: https://github.com/sponsors/pawamoy
[billing cycle]: https://docs.github.com/en/github/setting-up-and-managing-billing-and-payments-on-github/changing-the-duration-of-your-billing-cycle
[license]: ../license.md
[private forks]: https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/removing-a-collaborator-from-a-personal-repository

<script src="../js/insiders.js"></script>
<script>updateInsidersPage('pawamoy');</script>
