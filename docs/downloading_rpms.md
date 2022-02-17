# Downloading RPMs

You can download the latest RPMs using `wget`:

```
wget --recursive --no-parent -R "index.html*" 'http://54.247.135.67/product-builds/latest/cs9/'
```

The repository size is approximately 1.3G, which includes both aarch64 and x86_64 RPMs. This size might change as the package set evolves.
