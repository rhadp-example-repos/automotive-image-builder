# Contributing to the automotive-sig repository

## Cloning the main repository

1. From GitLab, click *Clone* and copy the URL of the [Automotive SIG repository](https://gitlab.com/redhat/automotive/automotive-sig). You can choose either SSH or HTTPS.
2. From a terminal window, clone the repository locally:
```
git clone <url> <shortname>
```
Example:
```
git clone git@gitlab.com:redhat/automotive/automotive-sig.git origin
```

## Creating a fork

1. From GitLab, click *Fork*.
2. Optional: Enter a project name. If you don't enter a project name, the fork inherits the name of the origin.
3. Select your name from the *namespace* menu.
4. Optional: Enter a project description.
5. Select your preferred visibility level.
6. Click *Fork project* to create your fork.

## Adding your fork as a remote

1. From GitLab, click *Clone* and copy the URL of your fork. You can choose either SSH or HTTPS.
2. From a terminal window, go to your clone of the automotive-sig repository and add your fork as a remote repository:
```
git remote add <fork-shortname> <url>
```
Example:
```
git remote add myfork git@gitlab.com:your-name/your-automotive-sig.git
```
3. Optional: Confirm that you added your fork as a remote:
```
git remote -v
```
!!! note

  You can run this command at any time to view details about all of the remotes in the cloned repository.

## Contributing to the repository

1. Create a dedicated branch on your fork:
```
git checkout -b <branch>
```
Example:
```
git checkout -b my-branch
```

2. Push updates to your fork:
```
git push <fork-shortname> <branch>
```
Example:
```
git push myfork my-branch
```
3. From the Automotive-SIG repository, click *New merge request*.
4. Select the main branch of the Automotive-SIG repository as the target.
5. Select the following merge options:
  - Delete source branch when merge request is accepted.
  - Squash commits when merge request is accepted.
6. Request a review from someone with maintainer rights so that they can review and merge your changes.
