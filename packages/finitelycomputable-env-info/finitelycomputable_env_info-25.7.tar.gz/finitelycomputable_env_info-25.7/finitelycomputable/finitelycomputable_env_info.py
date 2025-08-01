from importlib import import_module, metadata
from os import environ
from posixpath import join
from platform import python_version

base_path = join('/', environ.get('BASE_PATH', ''))
included_apps = {}
environment_text = environ.get('MICROSITES_VERSION_TEXT', '')

def include_app(name, app_path):
    ab_name = "finitelycomputable." + name
    pack_stem = "finitelycomputable-" + name.replace("_", "-")
    module = import_module(ab_name)
    pack = module.application.__module__
    dists = [d for d in metadata.packages_distributions()['finitelycomputable']
            if d.startswith(pack_stem)]
    if dists:
        dm = metadata.distribution(dists[0])
        included_apps[pack] = \
                f'<a href={app_path}>{dm.name}</a> version {dm.version}'
    else:
        included_apps[pack] = f'<a href={app_path}>{ab_name}</a> unknown version'
    return module

def index_html(app_h2, pkg):
    apps_list_items = '''</li>
  <li>'''.join(included_apps.values())
    dist = pkg.replace(".", "-").replace("_", "-")
    return (f'''<!DOCTYPE html><html><body>
<h1>Finitely Computable Microsites</h1>
<h2>{app_h2}</h2>
<a href="https://pypi.org/project/{dist}">{pkg}</a>
version {metadata.version(pkg)} is available on
<a href="https://pypi.org/">PyPi</a>
<h3>Installed Microsites</h3>
<ul>
  <li>{apps_list_items}</li>
</ul>
<a href="{join(base_path, "env_info")}">additional environment information</a>

<h3>Source Code</h3>
<ul>
  <li><a href="https://git.sr.ht/~thrasymache/finitelycomputable-microsites">
    Sourcehut
  </a></li>
  <li><a href="https://notabug.org/thrasymache/finitelycomputable-microsites">
    Notabug
  </a></li>
  <li><a href="https://gitlab.com/thrasymache/microsites">
    Gitlab
  </a></li>
  <li><a href="https://github.com/thrasymache/microsites">
    Github
  </a></li>
</ul>
</body></html>'''
        )

def env_html(framework, pkg):
    dist = pkg.replace(".", "-").replace("_", "-")
    dist_list_items = '''</li>
  <li>'''.join([f'{d.name} version {d.version}'
        for d in [metadata.distribution(j) for j in
            metadata.packages_distributions()['finitelycomputable']]
    ])
    apps_list_items = '''</li>
  <li>'''.join([f'{v} of {k}' for k, v in included_apps.items()])
    return (f'''<!DOCTYPE html><html><body>
Microsites Environment "{environment_text}"<br> using
<a href="https://pypi.org/project/{dist}/">{pkg}</a>
version {metadata.version(pkg)}
<br>on <a href="https://pypi.org/project/{framework}/">{framework}</a>
version {metadata.distribution(framework).version}<br>
on Python {python_version()}<br>
at {base_path} with the following apps
<ul>
  <li>{apps_list_items}</li>
</ul>
and the following finitelycomputable packages
<ul>
  <li>{dist_list_items}</li>
</ul>
</body></html>'''
        )
