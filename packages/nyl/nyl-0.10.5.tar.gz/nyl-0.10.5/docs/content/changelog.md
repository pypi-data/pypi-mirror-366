## 0.10.5 (2025-08-04)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Fix</td><td>

Allow extra keys on `ObjectMetadata`</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.10.3 (2025-05-08)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Improvement</td><td>

Further improve filtering of env vars that start with ARGOCD_ but are Kubernetes-specific</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Automatically drop empty `.metadata.labels` fields from resources generated with `nyl template` to prevent resources with such labels to immediately be `OutOfSync` after apply in ArgoCD</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.10.2 (2025-05-08)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Hygiene</td><td>

Rename `Manifest` and `Manifests` to `Resource` and `ResourceList` in codebase, and variable names/members accordingly</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Deprecation</td><td>

Remove `locals` from scope of template rendering, use `values` instead</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Feature</td><td>

Add support for `NYL_PYROSCOPE_*` environment variables.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Switch to using `python:3.13-slim` as base image instead of `python:3.13-alpine` to allow installing `pyroscope-io`, imag size is only marginally impacted</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Remove some Kubernetes-specific environment variables from log line that exposes Nyl-specific environment variables, and redact NYL_PYROSCOPE_URL</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.10.1 (2025-05-07)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Improvement</td><td>

Measure time of successful `nyl template` execution and log a line of level `"METRIC"` with a JSON metric payload</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Fan out evaluation of Nyl inline resources using ThreadPoolExecutor</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.10.0 (2025-05-07)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Improvement</td><td>

Remove `nyl argocd discovery` command and use a simpler yet probably sufficient `find` command in the `ConfigManagementPlugin` manifest instead</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

The ArgoCD CMP no longer logs to a file, users should check the pod logs instead</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Feature</td><td>

Add `nyl-daemon` command which can be used to launch and communicate with a Nyl daemon process to forego Python process launch times</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Support implicit default profile</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Disable waiting for API server connectivity for now when activating a profile as it seems to be more a hinderance than a useful feature</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.9.4 (2025-04-22)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Fix</td><td>

Fix previously breaking change that would cause a KeyError when the NYL_PROFILE environment variable was not set in the ArgoCD plugin when the project has no default profile.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.9.3 (2025-04-22)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Feature</td><td>

add support for `ARGOCD_ENV_NYL_PROFILE` environment variable</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.9.2 (2025-04-22)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Improvement</td><td>

Introduce new `values` object into templating evaluation namespace, replacing the `locals` object going forward. The `locals` name is still available but will be removed in an upcoming release.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Feature</td><td>

Allow defining parameters in the "values" of a profile, accessible via `${{ values.PARAM }}` throughout manifest rendering with the profile.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.9.1 (2025-04-20)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Improvement</td><td>

`nyl new component` now includes `metadata.labels` and `metadata.annotations` defaults in the generated `values.yaml`</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Feature</td><td>

Add support for `NYL_ARGS` and `ARGOCD_ENV_NYL_ARGS` environment variables</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Improve help text of `nyl new component` command</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

`.metadata.labels` set on a `HelmChart` resource now propagate and overwrite labels on the resources it generates (note that this also applies to Nyl components using Helm charts)</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.9.0 (2025-04-15)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Feature</td><td>

Add ability to define and use local variables in manifests</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

argocd-cmp: Upgrade ArgoCD from v2.13.1 to v2.14.10</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

argocd-cmp: Upgrade Helm from v3.16.3 to v3.17.3</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

argocd-cmp: Upgrade Sops from v3.9.2 to v3.10.2</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

argocd-cmp: Upgrade Kyverno from 1.13.2 to 1.13.4</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.8.1 (2025-01-22)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Fix</td><td>

Remove sneaky `breakpoint()` call in `nyl template`</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.8.0 (2025-01-22)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Improvement</td><td>

Further improve on #56 by populating the namespace of resources earlier than later (e.g. before the `HelmChart` gets rendered, instead of only applying it to the resources generated by the `HelmChart` at the end).</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.7.2 (2025-01-17)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Feature</td><td>

Add `nyl add namespace` command</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Docs</td><td>

Fix links in docs and add information on how to use the `HelmChart.spec.chart` field</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Feature</td><td>

Add `nyl add chart` command</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Docs</td><td>

Add note to discurage from using `{{ .Release.Namespace }}` in Helm charts</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Breaking change</td><td>

Rename annotation `nyl.io/default-namespace` to `nyl.io/is-default-namespace`</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.7.1 (2025-01-17)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Fix</td><td>

Fixed a bug where pulling two different charts with the same version number from the same repository conflated the cache key and ended up with Nyl using the wrong chart (that which has been pulled first).</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
</table>

## 0.7.0 (2025-01-17)

<table><tr><th>Type</th><th>Description</th><th>PR</th><th>Issues</th><th>Author</th></tr>
  <tr><td>Breaking change</td><td>

Recognize `nyl.io/default-namespace: "true"` on Namespace resources to choose between one of multiple namespaces defined in the same manifest file.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Breaking change</td><td>

Instead of not assuming a default namespace when multiple `Namespace` resources are defined in a manifest file, pick the first one alphabetically when none have the `nyl.io/default-namespace: "true"` annotation</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Apply Nyl `PostProcessor` instructions at the end, after Nyl had a chance to fill in the manifest file's determined default namespace. Kyverno might add the `namespace: default` field to any resource that has no namespace set, making it impossbile for Nyl after the fact to tell which resources need to have their namespace injected.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Fix</td><td>

Update `PostProcessor`, pointing Kyverno to a directory and expecting it to output all manifest, not just the mutated ones. The `PostProcessor` is now invoked at the very end, even after Nyl patches resources with the default namespace in the current manifest file.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Fix</td><td>

fix #57 -- `ARGOCD_APP_NAMESPACE` and the `--default-namespace` option are used now only when no namespace is defined in the manifest file</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Resources generated by the Nyl `HelmChart` resource now get the chart resource's `metadata.namespace` populated before they are passed up and inlined into the rest of the manifest. Fixes #56</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

Fix deprecation warnings of using the `loguru.logger.opt(ansi)` keyword argument and use the new `colors` kwarg instead</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Feature</td><td>

Add `PostProcessor.spec.kyvernoRules` field as a shorthand for defining Kyverno policies in a Nyl manifest.</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Refactor</td><td>

Refactor `PostProcessor` implementation for generating policy files and invoking Kyverno</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Improvement</td><td>

`PostProcessor` log for invoking Kyverno now lists the policy file paths that are going to be applied</td><td></td><td></td><td>@NiklasRosenstein</td></tr>
  <tr><td>Fix</td><td>

`nyl new chart` now generates 2-space indented YAML and has a more complete template</td><td></td><td><a href="https://github.com/NiklasRosenstein/nyl/issues/47">NiklasRosenstein/nyl#47</a></td><td>@NiklasRosenstein</td></tr>
</table>

