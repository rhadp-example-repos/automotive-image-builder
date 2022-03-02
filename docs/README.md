# Automotive SIG documentation

This git repository contains the needed sources (markdown format) used to
generate the Automotive SIG documentation website running at:
https://sigs.centos.org/automotive/

It uses [mkdocs](https://mkdocs.org) but with a specific
 [material](https://squidfunk.github.io/mkdocs-material) theme

## How to test locally
The easiest way is just to use podman and a container:

```
podman pull docker.io/squidfunk/mkdocs-material:latest
```

You can then enter the directory where you have cloned this repository
(where mkdocs.yml is) and then you can run the following development site
(that will automatically refresh on each new file/change) :

```
podman run --rm -it -p 8000:8000 -v ${PWD}:/docs:z squidfunk/mkdocs-material
```

You can now open your browser to http://localhost:8000 and you'll be able to
see `live` your edit/changes

## How to render/build the site as static pages

Still using same podman container, but instead call it like this :

```
podman run --rm -it -v ${PWD}:/docs:z squidfunk/mkdocs-material build

```

Worth knowing that the goal is to just develop locally , and then git commit/push
as the built site will automatically be rendered in the next minutes on public
website
