# -*- coding: utf-8 -*-

import os
import subprocess
import sys

import oyaml as yaml


# --------------------------------------------------------------------------------------


def load_env(infile):
    return yaml.load(infile, Loader=yaml.Loader)


def print_env(env):
    print(yaml.dump(env, Dumper=yaml.Dumper), file=sys.stdout)


def run(cmd):
    return subprocess.check_output(
        cmd, encoding="utf-8", shell=True, stderr=subprocess.STDOUT,
    ).strip()


def load_versions(env_name):

    cmd = f"conda list -n {env_name}"

    output = subprocess.check_output(
        cmd, encoding="utf-8", env=os.environ.copy(), shell=True
    ).strip()

    pkgs = {}

    for line in output.split("\n"):
        if line.startswith("#"):
            continue

        pkg, ver, *_ = line.split()
        pkgs[pkg] = ver

    return pkgs


def parse_pkg(pkg):
    comps = ("=", "<", ">")

    if "[" in pkg:
        return pkg.split("[")[0]
    elif any((c in pkg for c in comps)):
        for c in comps:
            pkg = pkg.replace(c, " ")
        return pkg.split()[0]
    return pkg


def strip_version(pkg):

    comps = {"=", "<", ">"}
    loc_comps = set(pkg) & comps

    if loc_comps:
        for c in loc_comps:
            pkg = pkg.replace(c, " ")
        pkg = pkg.split()[0]
    return pkg


def has_optional_installs(pkg):
    return "[" in pkg


def pin_version(pkgs_versions, pkg, pip=False):

    eq = "==" if pip else "="
    de_ver_pkg = strip_version(pkg)

    if has_optional_installs(de_ver_pkg):
        pkg_name = de_ver_pkg.split("[", 1)[0]
        ver = pkgs_versions.get(pkg_name, "?")
    else:
        ver = pkgs_versions.get(de_ver_pkg, "?")

    return "".join((de_ver_pkg, eq, ver))


def set_versions(pkgs_versions, deps, pip=False):
    for ix, pkg in enumerate(deps):
        deps[ix] = pin_version(pkgs_versions, pkg, pip=pip)


def has_dependencies(env):
    return "dependencies" in env


def split_dependencies(dependencies):
    """Separate Conda and Pip package dependencies."""

    ix = None
    for ix, item in enumerate(dependencies):
        if isinstance(item, dict) and "pip" in item:
            break

    pip = None
    if ix is not None:
        pip = dependencies.pop(ix)["pip"]

    return dependencies, pip


def write_versions(env):

    if has_dependencies(env):

        pkgs_versions = load_versions(env["name"])
        dependencies, pip = split_dependencies(env["dependencies"])

        set_versions(pkgs_versions, dependencies)

        if pip:
            set_versions(pkgs_versions, pip, pip=True)
            dependencies.append({"pip": pip})

    return env


def unversion(env):

    dependencies, pip = split_dependencies(env["dependencies"])
    dependencies = [strip_version(pkg) for pkg in dependencies]

    if pip:
        pip = [strip_version(pkg) for pkg in pip]
        dependencies.append({"pip": pip})

    env["dependencies"] = dependencies

    return env


def write_pkg_versions(infile, deversion=False):

    env = load_env(infile)

    if deversion:
        env = unversion(env)
    else:
        env = write_versions(env)

    print_env(env)
