# Automotive SIG documentation

This git repository contains the source files required to generate
the Automotive SIG documentation hosted at:
https://sigs.centos.org/automotive/

The source files are in markdown format. The repository uses [mkdocs](https://mkdocs.org) but with a specific
 [material](https://squidfunk.github.io/mkdocs-material) theme.

## Testing locally
Use podman and a container to test locally:

```
podman pull docker.io/squidfunk/mkdocs-material:latest
```

Enter the directory where you cloned this repository
(where mkdocs.yml is) and run the following development site, which automatically refreshes with each new file or change:

```
podman run --rm -it -p 8000:8000 -v ${PWD}:/docs:z squidfunk/mkdocs-material
```

Open a browser and navigate to http://localhost:8000 to
see your updates.

## Building the site as static pages

Using same podman container, run the following command:

```
podman run --rm -it -v ${PWD}:/docs:z squidfunk/mkdocs-material build

```

After you develop the content locally, git commit and push the changes. 
Within a few minutes, the built site will automatically be rendered
on the public website.
