let
  common = import ./common.nix { };
  pkgs = common.pkgs;

  appSource = pkgs.runCommand "chipollino-web-app" { } ''
    mkdir -p $out
    cp -r ${./accounts} $out/accounts
    cp -r ${./chipollino_web} $out/chipollino_web
    cp -r ${./converter} $out/converter
    cp -r ${./static} $out/static
    cp -r ${./templates} $out/templates
    cp ${./manage.py} $out/manage.py
    cp -r ${common.chipollino} $out/Chipollino
    cp -r ${common.configSrc} $out/config
    chmod -R u+w $out
  '';

  appRoot = pkgs.runCommand "chipollino-web-app-root" { } ''
    mkdir -p $out/app
    cp -r ${appSource}/. $out/app/
    chmod -R u+w $out/app
  '';

  entrypoint = pkgs.writeShellScriptBin "chipollino-web-entrypoint" ''
    set -e
    cd /app
    python manage.py migrate
    python manage.py collectstatic --noinput
    exec gunicorn --bind 0.0.0.0 --timeout 120 chipollino_web.wsgi
  '';

  rootContents = pkgs.buildEnv {
    name = "chipollino-web-root";
    paths = common.runtimePackages ++ [
      pkgs.bash
      pkgs.coreutils
      entrypoint
      appRoot
    ];
    ignoreCollisions = true;
  };

  appImage = pkgs.dockerTools.buildImage {
    name = "chipollino-web-app";
    tag = "latest";
    keepContentsDirlinks = true;

    copyToRoot = rootContents;

    config = {
      WorkingDir = "/app";
      Entrypoint = [ "/bin/chipollino-web-entrypoint" ];
      Env = [
        "PATH=${common.pythonEnv}/bin:${common.refal5}/bin:/bin"
        "DJANGO_DEBUG=0"
      ];
    };
  };

  caddyStatic = pkgs.runCommand "chipollino-web-caddy-static" { } ''
    mkdir -p $out/var/www/html/static
    cp -r ${./static}/. $out/var/www/html/static/
    chmod -R u+w $out
  '';

  caddyConfig = pkgs.writeTextDir "etc/caddy/Caddyfile" ''
    :8000 {
      root * /var/www/html
      file_server /static/* browse

      @notStatic {
        not path /static/*
      }

      reverse_proxy @notStatic http://app:8000
    }
  '';

  caddyRoot = pkgs.runCommand "chipollino-web-caddy-root" { } ''
    mkdir -p $out/bin $out/etc/caddy $out/var/www/html/static
    ln -s ${pkgs.caddy}/bin/caddy $out/bin/caddy
    cp ${caddyConfig}/etc/caddy/Caddyfile $out/etc/caddy/Caddyfile
    cp -r ${caddyStatic}/var/www/html/static/. $out/var/www/html/static/
  '';

  caddyImage = pkgs.dockerTools.buildImage {
    name = "chipollino-web-caddy";
    tag = "latest";

    copyToRoot = caddyRoot;

    config = {
      Cmd = [ "caddy" "run" "--config" "/etc/caddy/Caddyfile" "--adapter" "caddyfile" ];
    };
  };
in
pkgs.linkFarm "chipollino-web" [
  { name = "app"; path = appImage; }
  { name = "caddy"; path = caddyImage; }
]
