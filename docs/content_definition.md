# Content definition

The primary deliverable of the Automotive SIG is an RPM repository,
serving as the input to reference automotive image builds.  The
repository is defined as a subset of CentOS Stream, with a handful of
exceptions representing unique Automotive SIG content.  For example,
such exceptions could include additional packages not present in Stream
or override, differently built or configured packages in situations
where deviations are required.

The Automotive SIG relies on
[Content Resolver](https://tiny.distro.builders/)
to define and select content, using CentOS Stream and CBS repositories
as its dependency resolution backends.

## Definition layout

Content Resolver operates with four distinct types of input definitions:
repositories, environments, workloads, and views.

Repository definitions group one or more package repositories and assign
them priorities for dependency resolution.  The SIG uses CentOS Stream
repositories and CBS and COPR as fallbacks.  With this mechanism, we can
include packages not currently being part of Stream.

Environment definitions list top-level, standard packages expected in
every in-vehicle installation.  The Automotive environment includes a
set of packages needed to boot the system on the target hardware
platform, as well as additional components identified during functional
safety and security requirements reviews.  It represents the minimum
recommended installation footprint.

The purpose of workloads is to layer additional packages on top of the
essential in-vehicle environment or extend the Automotive repository
with new content potentially useful for development and testing.  The
two standard workloads we define are the in-vehicle and the off-vehicle
sets.  The former is empty, only inheriting the environment component
list, and the latter extends it with various development tools.
Additional experimental workloads may be added to visualize and analyze
the impact of including new packages.  See the section below for more
detail.

Finally, the view unifies the resolved workloads into a single, flat
list of packages.  The view effectively represents the Automotive
package repository and can be used to build them in practice.

The
[Content Resolver documentation](https://github.com/minimization/content-resolver#content-resolver)
may provide more insight into how all these input types tie together.

## Add your own

Adding new content to the deliverable is easy.  The recommended approach
is via defining a new workload extending the default environment.  The
definitions are managed on
[GitHub](https://github.com/minimization/content-resolver-input).

Use the `automotive` label to inherit the base in-vehicle environment
automatically and include the newly added package components into the
unified view.  Only top-level packages need to be listed, as the service
will automatically resolve dependencies.  Dependencies may still be
listed explicitly if your application depends on them, too.

If the workload requires content not present in Stream or CBS, add
additional repositories to the Automotive repository definition.  Use a
lower priority for the custom repositories to avoid masking content
coming from Stream or CBS.
